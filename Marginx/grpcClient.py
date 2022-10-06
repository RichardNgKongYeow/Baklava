from itertools import chain
from subprocess import list2cmdline
from decimal import Decimal
import utils
from fx_py_sdk.grpc_client import GRPCClient
from fx_py_sdk.builder import TxBuilder
from fx_py_sdk.codec.cosmos.base.v1beta1.coin_pb2 import Coin
from fx_py_sdk.codec.fx.dex.v1.order_pb2 import *
import decimal
from fx_py_sdk.codec.cosmos.tx.v1beta1.service_pb2 import BROADCAST_MODE_BLOCK, BROADCAST_MODE_SYNC
from google.protobuf.json_format import MessageToJson
import json
import logging


class grpcClient():
    
    CLIENT_NAME = "MarginXClient"

    def __init__(self,account:object, chain_id:str, configs):
        
        
        self.chain_id = chain_id
        self.pair_id = configs['chain_id'][chain_id]['pair_id']
        self.address = configs['chain_id'][chain_id]['address']
        
        
        self.account = account
        self.client = None
        self.marginx_chain_id = None
        self.account_info = None
        self.gas_price = None
        self.tx_builder = None


        
    def initialise_client(self):
        try:
            # client = GRPCClient("https://testnet-btc-grpc.marginx.io:9090")
            self.client = GRPCClient(f"https://testnet-{self.chain_id}-grpc.marginx.io:9090")
            self.marginx_chain_id = self.client.query_chain_id()
            logging.info('{}'.format(self.marginx_chain_id))
        except Exception as e:
            logging.error("{}, initialise {} client,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))


    def initialise_client_and_get_all_info(self):
        self.initialise_client()
        self.get_account_info()
        self.query_gas_price()
        self.build_tx_builder()


# --------------------------------------account info--------------------------------------

    def get_account_info(self)->object:
        """
        return account_info needed for TxBuilder
        """
        try:
            self.account_info = self.client.query_account_info(self.account.address)
        except Exception as e:
            logging.error("{},{}, get_account_info,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))


    # def get_account_sequence(self)->int:
    #     """
    #     return an account sequence int
    #     """
    #     try:
    #         self.get_account_info()
    #         return self.account_info.sequence
    #     except Exception as e:
    #         logging.error("{},{}, get_account_sequence,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))


    def query_gas_price(self):
        # query gas price
        gas_prices = self.client.query_gas_price()
        gas_denom = "USDT"
        self.gas_price = next((gas for gas in gas_prices if gas.denom == gas_denom), None)
        if self.gas_price is None:
            raise ValueError(f"Could not find on-chain gas pricing for denom: {gas_denom}")

    def build_tx_builder(self):
        # build tx_builder
        try:
            self.tx_builder = TxBuilder(account = self.account, 
            private_key = None, chain_id = self.marginx_chain_id, 
            account_number = self.account_info.account_number, gas_price = self.gas_price)
        except Exception as e:
            logging.error("{},{}, build_tx_builder,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))

# ===================================querying positions info==============================
    async def query_open_positions(self)->list:
            """
            query all open positions (list) of an account given a pair_id and corresponding client
            """
            try:
                positions = self.client.query_positions(
                        owner=self.account.address, pair_id=self.pair_id)
                return positions
            except Exception as e:
                logging.error("{},{},query_open_positions,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))

    
    async def get_open_long_position(self)->list:
        """
        get open long position info (list)
        """
        positions = await self.query_open_positions()
        try:
            if len(positions) > 0:
                for position in positions:
                    """
                    [
                        Position(
                            Id="4",
                            Owner="0x1056C9e553587AC23d3d54C8b1C2299Dd4093C72",
                            PairId="AAPL:USDT",
                            Direction="long",
                            EntryPrice=Decimal("157.930376"),
                            MarkPrice=Decimal("156.888"),
                            LiquidationPrice=Decimal("2.762266"),
                            BaseQuantity=Decimal("38.433"),
                            Margin=Decimal("5966.230016"),
                            Leverage=1,
                            UnrealizedPnl=Decimal("-40.061636"),
                            MarginRate=Decimal("0.025437"),
                            InitialMargin=Decimal("40574.393601"),
                            PendingOrderQuantity=Decimal("0"),
                        )
                    ]
                    """
                    if position[3] == "long":
                        return position
        except Exception as e:
            logging.error("{},{},get_open_long_position,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))
    

    async def get_open_long_position_amount(self)->Decimal:
        """
        return the open long position amount in int in Decimal form 
        """
        open_position = await self.get_open_long_position()
        try:  
            if open_position == None:
                open_position_amount = 0
            else:
                open_position_amount = Decimal(open_position[7])
            return open_position_amount
        except Exception as e:
            logging.error("{},{}, get_open_long_position_amount,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))

    def get_open_short_position(self)->list:
        """
        get open short position info (list)
        """
        positions = self.query_open_positions()
        try:
            if len(positions) > 0:
                for position in positions:
                    """
                    [
                        Position(
                            Id="4",
                            Owner="0x1056C9e553587AC23d3d54C8b1C2299Dd4093C72",
                            PairId="AAPL:USDT",
                            Direction="long",
                            EntryPrice=Decimal("157.930376"),
                            MarkPrice=Decimal("156.888"),
                            LiquidationPrice=Decimal("2.762266"),
                            BaseQuantity=Decimal("38.433"),
                            Margin=Decimal("5966.230016"),
                            Leverage=1,
                            UnrealizedPnl=Decimal("-40.061636"),
                            MarginRate=Decimal("0.025437"),
                            InitialMargin=Decimal("40574.393601"),
                            PendingOrderQuantity=Decimal("0"),
                        )
                    ]
                    """
                    if position[3] == "short":
                        return position
        except Exception as e:
            logging.error("{},{},get_open_short_position,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))

    # --------------------------------execute marginx transactions---------------------------
    async def open_long_position(self, direction, amount):
        """
        input trade info and execute order on marginX
        """
        # acc_seq = self.get_account_sequence()
        client = self.client
        pair_id = self.pair_id
        
        try:
            tx_response = client.create_order(
                tx_builder=self.tx_builder,
                # need to convert pid into list of str
                pair_id=pair_id,
                # ordertype
                direction=direction,
                # tokenprice
                price=0,
                # synTokenAmount
                base_quantity=Decimal(utils.from3dp(amount)),
                leverage=1,
                acc_seq=self.account_info.sequence,
                mode=BROADCAST_MODE_BLOCK,
            )
            events = json.loads(tx_response.raw_log)[0]['events']
            return events
        except:
            logging.error("{},{},open_long_position".format(self.CLIENT_NAME, self.chain_id))

        
    async def close_open_long_position(self, amount):
        pair_id = self.pair_id
        open_long_position = self.get_open_long_position()
        # acc_seq = self.get_account_sequence()

        try:
            tx_response = self.client.close_position(
                tx_builder = self.tx_builder, 
                pair_id = pair_id, 
                position_id = open_long_position.Id, 
                price = decimal.Decimal(0), 
                base_quantity = Decimal(utils.from3dp(amount)), 
                full_close = False, 
                acc_seq = self.account_info.sequence, 
                market_close = True, 
                mode=BROADCAST_MODE_BLOCK)
            events = json.loads(tx_response.raw_log)[0]['events']
            return events
        except:
            logging.error("{},{},close long position,{}".format(self.CLIENT_NAME, self.chain_id, tx_response.raw_log))
    
    
    async def close_open_short_position(self, amount):
        pair_id = self.pair_id
        open_short_position = self.get_open_short_position()
        # acc_seq = self.get_account_sequence()

        try:
            tx_response = self.client.close_position(
                tx_builder = self.tx_builder, 
                pair_id = pair_id, 
                position_id = open_short_position.Id, 
                price = decimal.Decimal(0), 
                base_quantity = Decimal(utils.from3dp(amount)), 
                full_close = False, 
                acc_seq = self.account_info.sequence, 
                market_close = True, 
                mode=BROADCAST_MODE_BLOCK)
            events = json.loads(tx_response.raw_log)[0]['events']
            return events
        except:
            logging.error("{},{},close short position,{}".format(self.CLIENT_NAME, self.chain_id, tx_response.raw_log))


    def get_mx_order_dict(self, events:list)->dict:
        """
        match this orderid with 
        price i have to loop through dex.order_fill ->agggregate the price
        """
        try:
            order_dict = {}
            for event in events:
                if 'type' in event and event['type']=='dex.order_fill':
                    for attr in event['attributes']:
                        if attr['key']=='deal_price':
                            price = attr['value']
                        elif attr['key']=='order_id':
                            order_id = attr['value']
                            order_dict[order_id] = price
            return order_dict
        except Exception as e:
            logging.error("{},{},get_mx_order_dict,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))


    def get_mx_price(self, order_id:str, order_dict:dict):
        """
        get deal price from order_dict
        """
        try:
            return order_dict[order_id]
        except Exception as e:
            logging.error("{},{},get_mx_price,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))



    def get_order_info(self,events:list)->tuple:
        """
        from events fx.dex.Order get total filled qty & get orderid
        """

        try:
            for event in events:
                if 'type' in event and event['type']=='fx.dex.Order':
                    for attr in event['attributes']:
                        if attr['key'] == 'order_id':
                            order_id_mx = attr['value']
                        elif attr['key'] == 'filled_quantity':
                            filled_quantity_mx = attr['value']
                        elif attr['key'] == 'pair_id':
                            pair_id_mx = attr['value']
                        elif attr['key'] == 'direction':
                            direction_mx = attr['value']
                
                
                # this is for closing open orders
                elif 'type' in event and event['type']=='dex.close_position_order':
                    for attr in event['attributes']:
                        if attr['key'] == 'order_id':
                            order_id_mx = attr['value']
                        elif attr['key'] == 'filled_quantity':
                            filled_quantity_mx = attr['value']
                        elif attr['key'] == 'pair_id':
                            pair_id_mx = attr['value']
                        elif attr['key'] == 'direction':
                            direction_mx = attr['value']
            return pair_id_mx, direction_mx, filled_quantity_mx, order_id_mx
        except Exception as e:
            logging.error("{},{},get_order_info,{},{}".format(self.CLIENT_NAME,self.chain_id, e,type(e)))
    

    async def log_order_info(self,events):
        # TODO check for other fees?
        try:
            pair_id_mx, direction_mx, filled_quantity_mx, order_id_mx = self.get_order_info(events)
            order_dict = self.get_mx_order_dict(events)
            price_mx = self.get_mx_price(order_id_mx, order_dict)
            logging.info("{},Execution of order of,{},{},{},{},{}".format(self.CLIENT_NAME, pair_id_mx, direction_mx, price_mx, filled_quantity_mx, order_id_mx))
        except:
            pass
    



# # 1. Market order
# acc_seq = get_account_sequence()
# tx_response = client.create_order(
#     tx_builder=tx_builder,
#     # need to convert pid into list of str
#     pair_id=pair_id,
#     # ordertype
#     direction="BUY",
#     # tokenprice
#     price=Decimal(".25"),
#     # synTokenAmount
#     base_quantity=Decimal("10.1"),
#     leverage=5,
#     acc_seq=acc_seq,
#     mode=BROADCAST_MODE_BLOCK,
# )

# order_id = None
# print(tx_response)
# events = json.loads(tx_response.raw_log)[0]['events']
# for event in events:
#     if 'type' in event and event['type']=='fx.dex.Order':
#         for attr in event['attributes']:
#             if attr['key']=='order_id':
#                 order_id = attr['value']
#                 break
#         break

# TODO uncomment the next section for cancellation of orders

# 2. Cancel order
# if order_id is not None:
#     acc_seq += 1
#     tx_response = client.cancel_order(
#         tx_builder=tx_builder,
#         order_id=order_id,
#         acc_seq=acc_seq,
#         mode=BROADCAST_MODE_BLOCK
#     )
#     # 0 means work, others number fail
#     if tx_response.code == 0:   
#         print(f"{order_id}")

# # 3. Close position order
# positions = client.query_positions(
#     owner=account.address,
#     pair_id=pair_id,
# )
# if len(positions) > 0:
#     for position in positions:
#         # 0: BOTH, 1: LONG, 2: SHORT (not sure)
#         if position.Direction == 1:
#             acc_seq += 1
#             client.close_position(
#                 tx_builder=tx_builder,
#                 pair_id=pair_id,
#                 position_id=positions[0].Id,
#                 price=Decimal(".27"),
#                 # close all positions
#                 base_quantity=position.BaseQuantity - position.PendingOrderQuantity,
#                 full_close=False,
#                 acc_seq=acc_seq,
#                 mode=BROADCAST_MODE_BLOCK
#             )




# -----------------------TODO uncomment this-----------------------------
# # 4. Get oracle price
# oracle_price = client.query_oracle_price(pair_id)
# print(oracle_price)
# # 5. Get mark price
# mark_price = client.query_mark_price(pair_id,False)
# print(mark_price)
# # 6. Query order?
# from fx_py_sdk.constants import Order

# # a. connect to database (if filled/cancelled, cannot find without database)
# order: Order = client.query_order(
#     order_id=order_id,
#     use_db=False,
#     include_trades=False
# )
# print(order)

# # b. listen to websocket

# # c. query_tx (NOT CONFIRMED)
# # client.query_tx(tx_hash=)
# account_orders: Order = client.query_orders_by_account(
#     address="0x374ece95a265e310282d0a624c50268271d2d66e",
#     page_index=0,
#     page_size=100
#     )
# print(f"account orders are{account_orders}")

