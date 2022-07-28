import os
import json
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
import re
import asyncio
import grpcClient


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


    # # Utilities
    # # -----------------------------------------------------------
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
    def get_event_vars(self, events):
        """
        return the vars from the event needed to build the tx on marginx
        """
    
        pid = events["args"]["pid"]
        order_id = events["args"]["orderId"]
        order_type = events["event"]
        amt = events["args"]["synTokenAmount"]
        pair_id = self.pairs[pid]


        if order_type == "MintSynToken":
            direction = "MarketBuy"
        elif order_type == "BurnSynToken":
            direction = "MarketSell"
        else:
            pass
        return pair_id, direction, amt, order_id
    
    
    # define function to handle events and print to the console
    async def handle_event(self, event):
        events = json.loads(Web3.toJSON(event))
        pair_id, direction, amt, order_id = self.get_event_vars(events)
        mx_order_id = await self.build_mx_tx(pair_id, direction, amt, grpcClient)
        print("Pair: {}, Direction: {}, Amount: {}, OrderId: {}, MX_OrderId: ".format(pair_id, direction, amt, order_id, mx_order_id))



    # asynchronous defined function to loop
    # this loop sets up an event filter and is looking for new entires for the "OpenOrder" event
    # this loop runs on a poll interval
    async def log_loop(self,event_filter, poll_interval):
        while True:
            for entry in event_filter.get_new_entries():
                await self.handle_event(entry)
                await asyncio.sleep(2)
            await asyncio.sleep(poll_interval)




    def build_mx_client(self,gchain_id, grpc: grpcClient):
        account = self.marginx_account
        client_list = self.client_list
        client = grpc.get_client(gchain_id,client_list)
        chain_id = client.query_chain_id()
        account_info = grpc.get_account_info(client,account)
        acc_seq = grpc.get_account_sequence(account_info)
        tx_builder = grpc.get_tx_builder(chain_id,account,account_info)
        return client, acc_seq, tx_builder


    async def build_mx_tx(self, pair_id, direction, amt, grpc: grpcClient):
        chain_id = grpc.convert_to_lower_case(pair_id.split(":")[0])
        print
        client, acc_seq, tx_builder = self.build_mx_client(chain_id, grpc)
        print(f"Client: {client}, Acc_seq: {acc_seq}, Tx_builder: {tx_builder}")
        print(client.query_chain_id())
        print(client.query_account_info(self.marginx_account.address))
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

        order_id = None
        # print("tx_response: {}, type: {}".format(tx_response,type(tx_response)))




        events = json.loads(tx_response.raw_log)[0]['events']

        # # Serializing json
        # json_object = json.dumps(events, indent=4)
        
        # # Writing to sample.json
        # with open("sample.json", "w") as outfile:
        #     outfile.write(json_object)


        for event in events:
            if 'type' in event and event['type']=='fx.dex.Order':
                for attr in event['attributes']:
                    if attr['key']=='order_id':
                        order_id = attr['value']
                        break
                break
        return order_id

