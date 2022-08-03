import os
import json
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
import re
import asyncio
import grpcClient
import logging


class BaklavaObject(object):

    def __init__(self, address, private_key, marginx_account, client_list, provider=None):
        self.address = Web3.toChecksumAddress(address)
        self.private_key = private_key
        self.provider = os.environ["PROVIDER"] if not provider else provider      
        self.provider = provider if not provider else provider
        self.marginx_account = marginx_account
        self.client_list = client_list
        
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

    ADDRESS = "0x1f2A2A8eBF8Ec7102Bf15cb6eC5629A9E05b410a"

    full_path = os.getcwd()
    ABI = json.load(open(full_path+'/BaklavaClient/assets/'+'SyntheticPool.json'))["abi"]


    MAX_APPROVAL_HEX = "0x" + "f" * 64
    MAX_APPROVAL_INT = int(MAX_APPROVAL_HEX, 16)
    ERC20_ABI = json.load(open(full_path+'/BaklavaClient/assets/'+'SafeERC20Upgradeable.json'))["abi"]

    pairs={0:"TSLA:USDT", 1:"AAPL:USDT", 2: "BTC:USDT", 3: "NFLX:USDT", 4:"GOOG:USDT", 5: "FB:USDT", 6: "AMZN:USDT", 7: "SPY:USDT", 8: "IWM:USDT", 9: "TQQQ:USDT", 10: "FX:USDT"}

    def __init__(self, address, private_key, marginx_account, client_list, provider=None):
        super().__init__(address, private_key, marginx_account, client_list, provider)
        self.contract = self.conn.eth.contract(
            address=Web3.toChecksumAddress(BaklavaClient.ADDRESS), abi=BaklavaClient.ABI)


    # Utilities
    # -----------------------------------------------------------
    def fromWei(self,value):
        return self.conn.fromWei(value, 'ether')

    def from3dp(self,value):
        return value * 10**(-3)


    # # TODO this part needs to confirm if taking in the right ERC20 contract and USB?
    # def _is_approved(self, token, amount=MAX_APPROVAL_INT):
    #     erc20_contract = self.conn.eth.contract(
    #         address=Web3.toChecksumAddress(token), abi=BaklavaClient.PAIR_ABI)
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

    # ==============================event listener==============================

    # -----------------------------listener filters------------------------------
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


    # --------------------------------event listener handler--------------------------
    def get_event_vars(self, events:dict)->tuple:
        """
        return the vars from the event needed to build the tx on marginx
        """
        try:
            pid = events["args"]["pid"]
            order_id = events["args"]["orderId"]
            order_type = events["event"]
            amt = events["args"]["synTokenAmount"]
            pair_id = self.pairs[pid]
            price = events["args"]["synTokenPrice"]


            if order_type == "MintSynToken":
                direction = "MarketBuy"
            elif order_type == "BurnSynToken":
                direction = "MarketSell"
            else:
                pass
            return pair_id, direction, price, amt, order_id
        except Exception as e:
            logging.error("failed to listen to smart contract events due to error: {} of type {}".format(e,type(e)))
    
    
    def convert_web3_to_json(self,event):
        try:
            result = json.loads(Web3.toJSON(event))
            return result
        except Exception as e:
            logging.error("failed to convert data to json due to error: {} of type {}".format(e,type(e)))



    # -----------------------------------queue system-------------------------------------
    
    async def add_event_to_queue(self,event,myQueue):
        """
        get event vars from smart contract listener and put it in the queue
        """
        events = self.convert_web3_to_json(event)
        pair_id, direction, price, amt, order_id = self.get_event_vars(events)
        # print("Putting new item into queue")
        await myQueue.put((pair_id, direction, amt, order_id))
        converted_price = self.fromWei(price)
        converted_amount = self.from3dp(amt)
        logging.info("Listening to order of Pair: {}, Direction: {}, Price: {}, Amount: {}, OrderId: {}".format(pair_id, direction, converted_price, converted_amount, order_id))




# ------------------------------------marginx part-------------------------------------


    def build_mx_txbuilder(self,gchain_id, grpc: grpcClient):
        """
        return the necessary building blocks for building the Tx
        """
        account = self.marginx_account
        client_list = self.client_list
        client = grpc.get_client(gchain_id,client_list)
        chain_id = client.query_chain_id()
        account_info = grpc.get_account_info(client,account)
        acc_seq = grpc.get_account_sequence(account_info)
        tx_builder = grpc.get_tx_builder(chain_id,account,account_info)
        return client, acc_seq, tx_builder



    async def execute_mx_tx(self, pair_id, direction, amt, grpc: grpcClient):
        """
        input trade info and execute order on marginX
        """
        chain_id = grpc.convert_to_lower_case(pair_id.split(":")[0])
        client, acc_seq, tx_builder = self.build_mx_txbuilder(chain_id, grpc)
        
        # print(f"Client: {client}, Acc_seq: {acc_seq}, Tx_builder: {tx_builder}")
        # print(client.query_chain_id())
        # print(client.query_account_info(self.marginx_account.address))
        try:
            tx_response = client.create_order(
                tx_builder=tx_builder,
                # need to convert pid into list of str
                pair_id=pair_id,
                # ordertype
                direction=direction,
                # tokenprice
                # price=grpcClient.Decimal(price*10**-8),
                price=0,
                # synTokenAmount
                base_quantity=grpc.Decimal(amt*10**-3),
                leverage=5,
                acc_seq=acc_seq,
                mode=grpc.BROADCAST_MODE_BLOCK,
            )

            # order_id = None
            events = json.loads(tx_response.raw_log)[0]['events']
            return events

        except Exception as e:
            logging.error("marginx tx failed: {} of type {}".format(e,type(e)))
        

    # TODO stop here at logging errors

    def get_mx_order_dict(self, events:list)->dict:
        # fx.dex.order can get total filled qty & get orderid
        # match this orderid with 
        # price i have to loop through dex.order_fill ->agggregate the price
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

    def get_mx_price(self, order_id:str, order_list:dict):
        try:
            return order_list[order_id]
        except Exception as e:
            logging.error("failed to get marginx price due to error: {} of type {}".format(e,type(e)))



    def get_order_info(self,events:list)->tuple:
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
            return pair_id_mx, direction_mx, filled_quantity_mx, order_id_mx
        except Exception as e:
            logging.error("failed to get marginx order info due to error: {} of type {}".format(e,type(e)))
    

    async def log_order_info(self,events):
        # TODO check for other fees?
        # TODO need to check if orderfilled?
        pair_id_mx, direction_mx, filled_quantity_mx, order_id_mx = self.get_order_info(events)
        order_list = self.get_mx_order_dict(events)
        price_mx = self.get_mx_price(order_id_mx, order_list)
        # print(pair_id_mx, direction_mx, filled_quantity_mx, order_id_mx,price_mx)
        logging.info("Execution of order of Pair: {}, Direction: {}, Price: {}, Amount: {}, OrderId: {}".format(pair_id_mx, direction_mx, price_mx, filled_quantity_mx, order_id_mx))


    # -----------------------------------queue system-------------------------------------
    async def get_item_from_queue(self,id,myQueue):
        while True:
            print("Consumer: {} attempting to get from queue".format(id))
            pair_id, direction, amt, order_id = await myQueue.get()
            # if order_id is None:
            #     break
            events = await self.execute_mx_tx(pair_id, direction, amt, grpcClient)
            await self.log_order_info(events)

# ---------------------------------------overall architecture------------------------------
    # asynchronous defined function to loop
    # this loop sets up an event filter and is looking for new entires for the "OpenOrder" event
    # this loop runs on a poll interval
    async def log_event_listener_loop(self,event_filter, poll_interval, myQueue):
        while True:
            for entry in event_filter.get_new_entries():
                await self.add_event_to_queue(entry,myQueue)
                await asyncio.sleep(2)
            await asyncio.sleep(poll_interval)

    async def log_event_executer_loop(self, poll_interval, myQueue):
        await asyncio.wait([self.get_item_from_queue(1,myQueue),self.get_item_from_queue(2,myQueue)])
        await asyncio.sleep(poll_interval)


# Building a cross-chain bridge from Baklava, an AVAX Defi farm to MarginX, a decentralized exchange
# Designed and programmed account analytics tools to track fund movements and account propagation patterns
# Deployed on-chain validator analytics tools to track and extrapolate validator rewards and commission