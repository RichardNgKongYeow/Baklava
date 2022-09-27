import os
import json
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
import re
import asyncio
import logging
import utils
from decimal import Decimal
import Pairs


class BaklavaObject(object):

    def __init__(self, configs, private_key, provider=None):
        self.configs = configs
        self.address = Web3.toChecksumAddress(configs['wallet_address'])
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

    ABI = json.load(open(os.getcwd()+'/BaklavaClient/assets/'+'SyntheticPool.json'))["abi"]


    MAX_APPROVAL_HEX = "0x" + "f" * 64
    MAX_APPROVAL_INT = int(MAX_APPROVAL_HEX, 16)

    pairs = Pairs.pairs
    chain_ids = Pairs.chain_ids


    def __init__(self, configs, private_key, provider=None):
        super().__init__(configs, private_key, provider)
        
        # self.configs = configs
        self.wallet_address = configs['wallet_address']
        self.synthetic_pool_address = configs['synthetic_pool_address']
        self.configs = configs

        self.contract = self.conn.eth.contract(
            address=Web3.toChecksumAddress(self.synthetic_pool_address), abi=BaklavaClient.ABI)

        # TODO this needs to change
        self.syntoken_object_dict = self.initialise_syntoken_object_dict()


    # ==============================event listener==============================

    # --------------------------------listener filters-------------------------------------
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
    def convert_web3_to_json(self,event):
        """
        convert result into json
        """
        try:
            result = json.loads(Web3.toJSON(event))
            return result
        except Exception as e:
            logging.error("Baklava Client--failed to convert data to json due to error: {} of type {}".format(e,type(e)))
    
    
    def get_event_vars(self, events:dict)->tuple:
        """
        return the vars from the event needed to build the tx on marginx
        """
        try:
            pid = events["args"]["pid"]
            order_id = events["args"]["orderId"]
            order_type = events["event"]
            amount = events["args"]["synTokenAmount"]
            pair_id = self.pairs[pid]
            price = events["args"]["synTokenPrice"]
            if order_type == "MintSynToken":
                direction = "MarketBuy"
            elif order_type == "BurnSynToken":
                direction = "MarketSell"
            else:
                pass
            return pair_id, direction, price, amount, order_id
        except Exception as e:
            logging.error("Baklava Client--failed to listen to smart contract events due to error: {} of type {}".format(e,type(e)))
    
    


    # -----------------------------------queue system-------------------------------------
    
    async def add_event_to_queue(self,event,myQueue):
        """
        get event vars from smart contract listener and put it in the queue
        """
        events = self.convert_web3_to_json(event)
        pair_id, direction, price, amount, order_id = self.get_event_vars(events)
        await myQueue.put((pair_id, direction, amount, order_id))
        converted_price = utils.fromWei(price)
        converted_amount = utils.from3dp(amount)
        logging.info("Baklava Client--Listening to order of Pair: {}, Direction: {}, Price: {}, Amount: {}, OrderId: {}".format(pair_id, direction, converted_price, converted_amount, order_id))



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


# ======================================synthetic token=====================================
    def initialise_syntoken_object_dict(self)->dict:
        # TODO have to change to constants.pair_info and get information
        try:
            client_dict = {}
            for chain_id in self.chain_ids:
                client = SynTClient(self.configs['chain_id'][chain_id]['address'],self.private_key, provider=self.provider)
                pair = self.configs['chain_id'][chain_id]['pair_id']
                client_dict[pair] = client
            return client_dict
        except Exception as e:
            logging.error("Baklava Client--failed to initialise syn token object dictionary due to: {} of type {}".format(e,type(e)))

    def get_syntoken_total_supply(self):
        try:
            total_supply_dict = {}
            for i in self.syntoken_object_dict:
                syntoken_obj = self.syntoken_object_dict[i]
                total_supply = syntoken_obj.get_total_supply()
                total_supply_dict[i] = total_supply
            return total_supply_dict
        except Exception as e:
            logging.error("Baklava Client--failed to get token supply from token contract object due to: {} of type {}".format(e,type(e)))



# --------------------------------------circulating supply---------------------------------
class SynTClient(BaklavaObject):

    full_path = os.getcwd()
    ABI = json.load(open(full_path+'/BaklavaClient/assets/'+'SynT.json'))["abi"]
    

    def __init__(self, address, private_key, provider=None):
        super().__init__(address, private_key, provider)
        self.contract = self.conn.eth.contract(
            address=Web3.toChecksumAddress(self.address), abi=SynTClient.ABI)


    def get_total_supply(self):
        """
        get total supply of token
        """

        return Decimal(utils.from3dp(self.contract.functions.totalSupply().call()))