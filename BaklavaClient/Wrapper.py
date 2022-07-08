import os
import json
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
import re
import asyncio
import grpcClient


class BaklavaObject(object):

    def __init__(self, address, private_key, provider=None):
        self.address = Web3.toChecksumAddress(address)
        self.private_key = private_key
        self.provider = os.environ["PROVIDER"] if not provider else provider      
        self.provider = provider if not provider else provider
        
        if re.match(r'^https*:', self.provider):
            provider = Web3.HTTPProvider(self.provider, request_kwargs={"timeout": 60})
        elif re.match(r'^ws*:', self.provider):
            provider = Web3.WebsocketProvider(self.provider)
        elif re.match(r'^/', self.provider):
            provider = Web3.IPCProvider(self.provider)
        else:
            raise RuntimeError("Unknown provider type " + self.provider)
        
        self.conn = Web3(Web3.HTTPProvider(self.provider))
        if not self.conn.isConnected():
            raise RuntimeError("Unable to connect to provider at " + self.provider)
        
        
        self.gasPrice = self.conn.toWei('50','gwei'),

    def _create_transaction_params(self, value=0, gas=1500000):
        return {
            "from": self.address,
            "value": value,
            'gasPrice': 1,
            "gas": gas,
            "nonce": self.conn.eth.getTransactionCount(self.address),
        }

    def _send_transaction(self, func, params):
        tx = func.buildTransaction(params)
        signed_tx = self.conn.eth.account.signTransaction(tx, private_key=self.private_key)
        return self.conn.eth.sendRawTransaction(signed_tx.rawTransaction)


class BaklavaClient(BaklavaObject):

    ADDRESS = "0x22ab1a6A6010b2EF7cf6Bf75C579A6E4de6bE7ef"

    full_path = os.getcwd()
    ABI = json.load(open(full_path+'/BaklavaClient/assets/'+'SyntheticPool.json'))


    MAX_APPROVAL_HEX = "0x" + "f" * 64
    MAX_APPROVAL_INT = int(MAX_APPROVAL_HEX, 16)
    ERC20_ABI = json.load(open(full_path+'/BaklavaClient/assets/'+'ERC20.json'))["abi"]

    pairs={0:"TSLA:USDT", 1:"AAPL:USDT", 2: "BTC:USDT", 3: "NFLX:USDT", 4:"GOOG:USDT", 5: "FB:USDT", 6: "AMZN:USDT", 7: "SPY:USDT", 8: "IWM:USDT", 9: "TQQQ:USDT", 10: "FX:USDT"}

    def __init__(self, address, private_key, provider=None):
        super().__init__(address, private_key, provider)
        self.contract = self.conn.eth.contract(
            address=Web3.toChecksumAddress(BaklavaClient.ADDRESS), abi=BaklavaClient.ABI)


    # # Utilities
    # # -----------------------------------------------------------
    # # TODO this part needs to confirm if taking in the right ERC20 contract and USB?
    # def _is_approved(self, token, amount=MAX_APPROVAL_INT):
    #     erc20_contract = self.conn.eth.contract(
    #         address=Web3.toChecksumAddress(token), abi=BaklavaClient.ERC20_ABI)
    #     print(erc20_contract, token)
    #     approved_amount = erc20_contract.functions.allowance(self.address, self.router.address).call()
    #     return approved_amount >= amount

    # def is_approved(self, token, amount=MAX_APPROVAL_INT):
    #     return self._is_approved(token, amount)

    # def approve(self, token, max_approval=MAX_APPROVAL_INT):
    #     if self._is_approved(token, max_approval):
    #         return

    #     print("Approving {} of {}".format(max_approval, token))
    #     erc20_contract = self.conn.eth.contract(
    #         address=Web3.toChecksumAddress(token), abi=BaklavaClient.ERC20_ABI)

    #     func = erc20_contract.functions.approve(self.router.address, max_approval)
    #     params = self._create_transaction_params()
    #     tx = self._send_transaction(func, params)

    #     # wait for transaction receipt
    #     self.conn.eth.waitForTransactionReceipt(tx, timeout=6000)  # TODO raise exception on timeout





# ------------------------------------Read-Only Functions-----------------------------------

    def getSystemCoin(self):
        """
        get system coin address
        """
        return self.contract.functions.getSystemCoin().call()

# -----------------------------------utils------------------------------------------
    def divide_by_base_10(self,number,base):
        """
        takes in a number and divide it by the base 10 amount
        """
        return number*10**(-base)

# -------------------------------event listener--------------------------------------
    def get_event_vars_for_mxtx(self, events):
        """
        takes in an event and extracts the information required for building the tx
        """
    # syntokenamount TODO make this market order
        pid = events["args"]["pid"]
        order_id = events["args"]["orderId"]
        order_type = events["args"]["orderType"]
        price = events["args"]["synTokenPrice"]
        pair_id = self.pairs[pid]
        if order_type == 0:
            base_quantity = events["args"]["minSynTokenAmount"]
            direction = "BUY"
        elif order_type == 1:
            base_quantity = events["args"]["minSystemCoinAmount"]
            direction = "SELL"
        else:
            pass
        return pair_id, direction, price, base_quantity, order_id


    def handle_event(self, event):
        """
        return the necessary variables after taking in the event
        """
        events = json.loads(Web3.toJSON(event))
        pair_id, direction, price, base_quantity, order_id = self.get_event_vars_for_mxtx(events)
        return pair_id, direction, price, base_quantity, order_id


    async def log_loop(self,event_filter, poll_interval, queue: asyncio.Queue = None):
        # asynchronous defined function to loop
        # this loop sets up an event filter and is looking for new entires for the "OpenOrder" event
        # this loop runs on a poll interval
        asyncio.ensure_future()

        while True:
            for entry in event_filter.get_new_entries():



            # # for entry in event_filter.get_all_entries():
            #     pair_id, direction, price, base_quantity, order_id = self.handle_event(entry)
            #     queue.put_nowait((pair_id, direction, base_quantity, order_id))
                await asyncio.sleep(2)
                # return pair_id, direction, price, base_quantity, order_id
            await asyncio.sleep(poll_interval)

    def create_oo_event_filter(self):
        """
        create_open_order_event_filter        
        """
        return self.contract.events.OpenOrder.createFilter(fromBlock='latest')

    def create_co_event_filter(self):
        """
        create_cancel_order_event_filter        
        """
        return self.contract.events.CancelOrder.createFilter(fromBlock='latest')


    def create_mst_event_filter(self):
        """
        create_MintSynTokn_event_filter        
        """
        return self.contract.events.MintSynToken.createFilter(fromBlock='latest')


    def create_bst_event_filter(self):
        """
        create_BurnSynToken_event_filter        
        """
        return self.contract.events.BurnSynToken.createFilter(fromBlock='latest')

    # async def run_all_event_listener(self):
    #     oo_event_filter = self.contract.events.OpenOrder.createFilter(fromBlock='latest')
    #     co_event_filter = self.contract.events.CancelOrder.createFilter(fromBlock='latest')
    #     loop = asyncio.get_event_loop()
    #     f1 = loop.create_task(self.log_loop(oo_event_filter, 2))
    #     f2 = loop.create_task(self.log_loop(co_event_filter, 2))
    #     await asyncio.wait([f1,f2])
    #     print(f1,f2)


    def build_mx_tx(self,pair_id,direction,price,base_quantity):
        """
        takes in the params and builds the tx on marginx
        """

        acc_seq = grpcClient.get_account_sequence()
        tx_response = grpcClient.client.create_order(
            tx_builder=grpcClient.tx_builder,
            # need to convert pid into list of str
            pair_id=pair_id,
            # ordertype
            direction=direction,
            # tokenprice
            price=grpcClient.Decimal(self.divide_by_base_10(price,8)),
            # synTokenAmount
            base_quantity=grpcClient.Decimal(self.divide_by_base_10(base_quantity,3)),
            leverage=5,
            acc_seq=acc_seq,
            mode=grpcClient.BROADCAST_MODE_BLOCK,
        )


        # print(tx_response)
        events = json.loads(tx_response.raw_log)[0]['events']
        for event in events:
            if 'type' in event and event['type']=='fx.dex.Order':
                for attr in event['attributes']:
                    if attr['key']=='order_id':
                        order_id = attr['value']
        return order_id


    _oo_queue = asyncio.Queue()
    _co_queue = asyncio.Queue()


    async def queue_smart_k_event(self,myQueue:object, pair_id, direction, price, base_quantity, order_id):
        while True:
            await asyncio.sleep(1)
            print("Putting new item into queue")
            await myQueue.put(pair_id, direction, price, base_quantity, order_id)

    async def get_smart_k_event(self,id,myQueue):
        while True:
            print("Consumer: {} attempting to get from queue".format(id))
            pair_id, direction, price, base_quantity, order_id = await myQueue.get()
            if pair_id is None:
                break
            # print("Consumer: {} consumed article with id: {}".format(id,item))
            return id, pair_id, direction, price, base_quantity, order_id

    # async def run_oo_co_listeners(self):
    #     loop = asyncio.get_event_loop()
    #     f1 = asyncio.ensure_future(self.log_loop(self.create_oo_event_filter(), 2, self._oo_queue))
    #     f2 = asyncio.ensure_future(self.log_loop(self.create_co_event_filter(), 2, self._co_queue))
    #     await asyncio.wait(f1, f2)
    #     return f1,f2

    async def query_order(self,order_id):
        resp = grpcClient.query_order(order_id=order_id)
        return resp