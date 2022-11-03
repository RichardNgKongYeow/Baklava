import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal
import logging
import os
from queue import Queue
import threading
import traceback
from typing import Any, Callable, Dict, List, Optional, Union
from functools import partial
from eth_account import Account

from fx_py_sdk.builder import TxBuilder
from fx_py_sdk.codec.cosmos.auth.v1beta1.auth_pb2 import BaseAccount
from fx_py_sdk.codec.cosmos.tx.v1beta1.service_pb2 import BROADCAST_MODE_SYNC
from fx_py_sdk.codec.cosmos.base.v1beta1.coin_pb2 import Coin
from fx_py_sdk.grpc_client import GRPCClient, DEFAULT_DEC
from fx_py_sdk.constants import Position, Order
from fx_py_sdk.model.model import Trade, FundingTransfer
from core.data_type.common import OrderType, PositionAction, PositionSide

from logger.logger import HummingbotLogger
import connector.derivative.fx_dex.constants as CONSTANTS
from connector.derivative.fx_dex.constants import GasDenom
import time


client_logger = None
MEMPOOL_WAIT_INTERVAL = 5.0

class FxDexClientWrapper:
    @classmethod
    def logger(cls) -> HummingbotLogger:
        global client_logger
        if client_logger is None:
            client_logger = logging.getLogger(__name__)
        return client_logger

    def __init__(self,
                 seed: str,
                 grpc_url: str = None,
                 gas_denom: str = GasDenom.USDT,
                 debug_mode: bool = False):

        self._initialized = False

        # Set variables
        self._seed = seed
        self._debug_mode = debug_mode
        self._loop = asyncio.get_event_loop()
        self._gas_price = None

        # Instantiate GRPC Client
        self._init_client(grpc_url, gas_denom)

        # Create asyncio lock for account sequence
        self._acc_seq_semaphore = asyncio.Semaphore()


    @property
    def seed(self) -> str:
        return self._seed

    @property
    def client_address(self) -> str:
        return self._client_address

    @property
    def account_sequence(self) -> int:
        return self._account_sequence

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def gas_price(self) -> Coin:
        return self._gas_price

    def _get_account_sequence(self,
                              client_address: Optional[str] = None) -> int:
        """Gets account sequence from DEX."""
        return self.client.query_account_info(
            address = client_address or self._client_address
        ).sequence

    def _init_client(self,
                     grpc_url: str,
                     gas_denom: str) -> BaseAccount:
        """
        Initializes GRPC client using `self._private_key`.
        :param grpc_url: Tendermint GRPC URL endpoint
        :return: BaseAccount
        """
        self.client = GRPCClient(grpc_url)

        try:
            chain_id = self.client.query_chain_id()

            Account.enable_unaudited_hdwallet_features()
            account = Account.from_mnemonic(self._seed)
            account_info = self.client.query_account_info(account.address)
            self._client_address = account.address

            # Set account sequence
            self._account_sequence = self._get_account_sequence()

            # Retrieve chain-defined gas price
            gas_prices = self.client.query_gas_price()
            gas_price = next((gas for gas in gas_prices if gas.denom == gas_denom), None)
            if gas_price is None:
                raise ValueError(f"Could not find on-chain gas pricing for denom: {gas_denom}")
            else:
                self._gas_price = gas_price

            # Create and set TxBuilder
            self._tx_builder = TxBuilder(
                account=account,
                private_key=None,
                chain_id=chain_id,
                account_number=account_info.account_number,
                gas_price=gas_price,
            )
            self._initialized = True

        except Exception as ex:
            logging.error(f'Could not create TxBuilder for signing transactions\n{ex}', exc_info=True)
            return

        return account

    async def _send_tx(self,
                       tx_func: Callable,
                       retry_times: int = 3):
        """
        Provides `acc_seq` parameter and broadcasts Tx in threadsafe manner, and increments account sequence after success.
        In the event of an error it self-rectifies the cached account sequence.

        :param tx_func: `partial` function with all parameters supplied except `acc_seq`
        :retry_times: Number of times to retry sending transaction before giving up
        :return: tx_response
        """
        tx_response = None

        async with self._acc_seq_semaphore:
            if self._debug_mode:
                ex = None
                t0 = time.time()

            for retry in range(retry_times):
                try:
                    tx_response = await self._loop.run_in_executor(None, lambda:
                        tx_func(acc_seq=self._account_sequence)
                    )

                    # code == 0 indicates success
                    if not tx_response:
                        # Something strange happened, potentially network issue
                        self._account_sequence = self._get_account_sequence()
                    elif tx_response.code == 0:
                        # Increment by one for use in next transaction
                        self._account_sequence += 1
                        break
                    elif tx_response.code == 20:
                        # Mempool is full, not ideal to continue sending txs
                        # TO-DO: Notify FxDexDerivative so trading logic can be paused
                        self.logger().error(f"Error sending transaction (code: {tx_response.code}, mempool is full)")
                        await asyncio.sleep(MEMPOOL_WAIT_INTERVAL)
                    else:
                        # Report error
                        error_message = f'Error sending transaction (raw_log: {tx_response.raw_log}) (code: {tx_response.code})'
                        self.logger().error(error_message)

                        # No point retrying if error code is fatal
                        if tx_response.code in CONSTANTS.FATAL_ERROR_CODES:
                            break

                        # For incorrect account sequence, set sequence to expected number
                        # In other cases, set it to the on-chain sequence
                        if 'incorrect account sequence' in tx_response.raw_log:
                            self._account_sequence = int(tx_response.raw_log.split(',')[1].split(' ')[-1])
                        else:
                            self._account_sequence = self._get_account_sequence()

                        if retry == retry_times - 1:
                            raise Exception(error_message)
                except Exception as e:
                    logging.error(f'Error sending transaction {traceback.format_exc()}')
                    self._account_sequence = self._get_account_sequence()
                    ex = e

            if self._debug_mode:
                t1 = time.time()
                tx_name = tx_func.func.__name__
                retry_log = f" (Retried {retry+1} times)" if retry>0 else ""
                exception_log = f" (Exception: {ex})" if ex else ""

                self.logger().info(
                    f"{t1 - t0:.3f}s executing transaction {tx_name}{retry_log}{exception_log}"
                )

        return tx_response

    async def place_order(self,
                          market: str,
                          side: PositionSide,
                          amount: Decimal,
                          price: Decimal,
                          position_action: PositionAction,
                          leverage: int = None,
                          position_id: Union[str, int] = None,
                          broadcast_mode: int = BROADCAST_MODE_SYNC,
                          order_type: OrderType = OrderType.LIMIT):
        """
        Places order on exchange.

        :param market: Exchange trading pair
        :param side: LONG or SHORT. Ignored for closing orders.
        :param amount: Order quantity (quoted in base asset)
        :param price: Price of base asset
        :param position_action: OPEN or CLOSE.
        :param leverage: Order leverage
        :param position_id: Position ID of closing order. Ignored for opening orders.
        :param broadcast_mode: Tendermint broadcast mode, SYNC preferred.

        :return: tx_response
        """
        try:
            # self.logger().info(f"{amount} @ {price}")

            if position_action == PositionAction.OPEN:
                """Send open position order"""
                if order_type == OrderType.LIMIT:
                    direction = "BUY" if side==PositionSide.LONG else "SELL"
                elif order_type == OrderType.MARKET:
                    direction = "MarketBuy" if side==PositionSide.LONG else "MarketSell"
                    # price = Decimal("0")

                return await self._send_tx(
                    partial(self.client.create_order,
                        tx_builder=self._tx_builder,
                        pair_id=market,
                        direction=direction,
                        price=price,
                        base_quantity=amount,
                        leverage=leverage,
                        mode=broadcast_mode)
                )

            elif position_action == PositionAction.CLOSE:
                """Send close position order"""
                market_close = order_type == OrderType.MARKET
                # if market_close:
                #     price = Decimal("0")

                return await self._send_tx(
                    partial(self.client.close_position,
                        tx_builder=self._tx_builder,
                        pair_id=market,
                        position_id=str(position_id),
                        price=price,
                        base_quantity=amount,
                        full_close=False,
                        market_close=market_close,
                        mode=broadcast_mode)
                )

            else:
                """Raise error in event of invalid position_action"""
                raise ValueError(f"Invalid position_action: ", position_action)

        except Exception as e:
            self.logger().error(f"Unable to place order {e}")

    async def cancel_order(self,
                           order_id: str,
                           broadcast_mode=BROADCAST_MODE_SYNC):
        """
        Cancels order on exchange.
        :param order_id: Exchange order ID (e.g. ID-1727996-13)
        :param broadcast_mode: Tendermint broadcast mode, BROADCAST_MODE_SYNC preferred.
        :return: tx_response
        """
        try:
            tx_response = await self._send_tx(
                partial(self.client.cancel_order,
                    tx_builder=self._tx_builder,
                    order_id=order_id,
                    mode=broadcast_mode)
            )
            return tx_response
        except Exception as e:
            logging.error(f"unable to cancel order {order_id}", e)

    async def get_orderbook_snapshot(self,
                                     pair_id: str) -> Dict[str, Any]:
        """
        Gets orderbook snapshot.
        :param pair_id: Exchange trading pair (e.g. TSLA:USDT)
        :return: Dict, e.g.
        { "Asks": [ {"price": "1157.170", "quantity": "1.0"} ],
          "Bids": [ {"price": "1156.120", "quantity": "1.0"} ] }
        """        
        orderbook = await self._loop.run_in_executor(None,
            lambda: self.client.query_orderbook(
                pair_id = pair_id
            )
        )

        for side in ["Asks", "Bids"]:
            orders = orderbook[side]
            for i, order in enumerate(orders):
                orders[i] = { k: Decimal(v) / DEFAULT_DEC for k, v in order.items() }

        return orderbook

    async def get_positions(self,
                            pair_id: str,
                            client_address: Optional[str] = None) -> List[Position]:
        """
        Gets list of positions from DEX.
        :param pair_id: Exchange trading pair (e.g. GOOG:USDT)
        :param client_address: Optional, defaults to initialized's address
        :return: List of Positions
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_positions(
                owner = client_address or self._client_address,
                pair_id = pair_id
            )
        )

    async def get_balances(self,
                           client_address: Optional[str] = None) -> Dict[str, int]:
        """
        Gets dictionary of balances from DEX.
        :param client_address: Optional, defaults to initialized's address
        :return: Dict of balances, e.g. { 'FX': 1.0, 'USDT': 100.0 }
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_all_balances(
                address = client_address or self.client_address
            )
        )


    async def get_mark_prices(self,
                              pair_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Gets single mark price (for one pair_id) or all mark prices
        :param pair_id: Optional, defaults to all trading pairs
        :return: Dict, e.g. { 'pairMarkPrice': [{'pairId': 'TSLA:USDT', 'price': '1130.675'}] }
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_mark_price(
                pair_id = pair_id,
                query_all = pair_id is None
            )
        )

    async def get_oracle_price(self,
                               pair_id: str) -> Decimal:
        """
        Gets oracle price for a trading pair.
        :param pair_id: Exchange trading pair (e.g. GOOG:USDT)
        :return: Oracle price
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_oracle_price(
                pair_id = pair_id
            )
        )

    async def get_funding_times(self) -> Dict[str, Any]:
        """
        Synchronous call to get funding metadata from DEX.
        :return: Funding info dictionary. Fields include fundingPeriod, nextFundingTime,
        fundingTimes, nextLogTime, logFundingPeriod, maxFundingPerBlock
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_funding_info()
        )

    def get_funding_times_sync(self) -> Dict[str, Any]:
        """
        Synchronous call to get funding metadata from DEX.
        :return: Funding info dictionary. Fields include fundingPeriod, nextFundingTime,
        fundingTimes, nextLogTime, logFundingPeriod, maxFundingPerBlock
        """
        return self.client.query_funding_info()

    async def get_funding_info(self,
                               pair_id: str) -> Dict[str, Any]:
        """
        Gets next funding time and current funding rate estimate.
        :param pair_id: Exchange trading pair (e.g. GOOG:USDT)
        :return: Dict, e.g. {'pairFundingRates': {'pairId': 'TSLA:USDT', 'fundingRate': '0.013', 'fundingTime': '1639474025'}}
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_funding_rate(
                last_or_realtime=False
            )
        )

    async def get_previous_funding_info(self,
                                        pair_id: str) -> Dict[str, Any]:
        """
        Gets previous funding rate at settlement.
        :param pair_id: Exchange trading pair (e.g. GOOG:USDT)
        :return: Dict, e.g. {'pairFundingRates': {'pairId': 'TSLA:USDT', 'fundingRate': '0.013', 'fundingTime': '1639474025'}}
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_funding_rate(
                last_or_realtime=True
            )
        )

    async def get_trades(self,
                         order_id: str,
                         pair_id: str = None) -> List[Trade]:
        """
        (From database) Queries order fills for an order_id.
        :param order_id: Exchange order ID (e.g. ID-1727996-13)
        :return: List of Trades
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_trades(
                pair_id = pair_id,
                order_id = order_id,
            )
        )

    async def get_order(self, 
                        order_id: str,
                        pair_id: str = None,
                        use_db: bool = False) -> Order:
        """
        Queries order from DEX. Can only retrieve pending orders.
        :param order_id: Exchange order ID (e.g. ID-1727996-13)
        :return: Order
        """
        if self._debug_mode and use_db:
            t0 = time.time()
        
        order = await self._loop.run_in_executor(None,
            lambda: self.client.query_order(
                pair_id = pair_id,
                order_id = order_id,
                use_db = use_db
            )
        )

        if self._debug_mode and use_db:
            t1 = time.time()
            self.logger().info(f"Getting order {order_id} took {t1 - t0:.3f}s")

        return order

    async def get_orders(self,
                         trading_pair: str,
                         client_address: Optional[str] = None) -> List[Order]:
        """
        Queries order from DEX. Can only retrieve pending orders.
        :param order_id: Exchange order ID (e.g. ID-1727996-13)
        :return: Order
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_orders(
                owner = client_address or self.client_address,
                pair_id = trading_pair,
                page = "1",
                limit = "10000"
            )
        )

    async def get_chain_id(self) -> str:
        """Queries blockchain ID."""
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_chain_id()
        )

    async def get_funding_payments(self,
                                   address: str,
                                   market: str,
                                   from_ts: float) -> List[FundingTransfer]:
        """
        (From database) Queries historical funding payments for a user and pair_id.
        :param address: Client address of payment owner
        :param pair_id: Exchange trading pair (e.g. TSLA:USDT)
        :param from_ts: UNIX timestamp to query from
        :return: List of funding transfers
        """
        try:
            return await self._loop.run_in_executor(None,
                lambda: self.client.crud.get_funding_transfers(
                    address = address,
                    pair_id = market,
                    from_datetime = datetime.utcfromtimestamp(from_ts)
                )
            )
        except:
            return []

    async def get_exposures(self,
                            addresses: Optional[List[str]] = None) -> Dict[str, Decimal]:
        """Dollar exposure of all wallets. Returns Dictionary of wallet addr -> dollar exposure."""        
        return self.client.crud.get_dollar_exposure(addresses)

    async def get_contract_exposures(self,
                                     addresses: Optional[List[str]] = None):
        """Contract exposure of all wallets. Returns Dictionary of wallet addr -> contract exposure."""
        return self.client.crud.get_contract_exposure(addresses)

    async def get_tx(self, tx_hash: str):
        """
        Queries Tx details from DEX. Useful when using `BROADCAST_MODE_SYNC`.
        However, it works only after Tx is confirmed—there is a time interval between `CheckTx` and `Commit`.

        :param tx_hash: Tx Hash, can be inferred from `tx_response.txhash`
        :return: tx_response
        """
        return await self._loop.run_in_executor(None,
            lambda: self.client.query_tx(
                tx_hash = tx_hash
            )
        )

    async def get_all_accounts(self) -> List[BaseAccount]:
        accounts = []
        account_results = await self._loop.run_in_executor(None,
            lambda: self.client.query_accounts(0)
        )

        for account_any in account_results:
            account = BaseAccount()
            if account_any.Is(account.DESCRIPTOR):
                account_any.Unpack(account)
            
            accounts.append(account)

        return accounts

cli_logger = None
class FxDexClientWrapperFactory:
    _client = None

    @classmethod
    def logger(cls) -> HummingbotLogger:
        global cli_logger
        if cli_logger is None:
            cli_logger = logging.getLogger(__name__)
        return cli_logger

    @classmethod
    def get_client(cls,
                   seed: str = None,
                   grpc_url: str = None,
                   gas_denom: str = GasDenom.USDT,
                   debug_mode: bool = False) -> FxDexClientWrapper:
        """
        Factory method that returns a single (shared) client instance across application
        :param: 24-word mnemonic, defaults to `FXDEX_PRIVATE_KEY` environment var
        :param: GRPC endpoint URL, defaults to `TESTNET_GRPC_URL` environment var
        :return: FxDexClientWrapper
        """
        if not cls._client:
            seed = seed or os.environ["SEED"]
            grpc_url = grpc_url or CONSTANTS.GRPC_URL
            cls.logger().info(grpc_url)
            cls._client = FxDexClientWrapper(seed, grpc_url, gas_denom, debug_mode)

            cls.logger().info(f"Initialized client wrapper with {cls._client.client_address}")

        return cls._client
