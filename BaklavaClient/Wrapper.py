import os
import json
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
import re


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

    ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"

    ABI = json.load(open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/assets/" + "IUniswapV2Factory.json")))["abi"]

    ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    ROUTER_ABI = json.load(open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/assets/" + "IUniswapV2Router02.json")))["abi"]

    MAX_APPROVAL_HEX = "0x" + "f" * 64
    MAX_APPROVAL_INT = int(MAX_APPROVAL_HEX, 16)
    ERC20_ABI = json.load(open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/assets/" + "IUniswapV2ERC20.json")))["abi"]

    PAIR_ABI = json.load(open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/assets/" + "IUniswapV2Pair.json")))["abi"]

    def __init__(self, address, private_key, provider=None):
        super().__init__(address, private_key, provider)
        self.contract = self.conn.eth.contract(
            address=Web3.toChecksumAddress(BaklavaClient.ADDRESS), abi=BaklavaClient.ABI)
        self.router = self.conn.eth.contract(
            address=Web3.toChecksumAddress(BaklavaClient.ROUTER_ADDRESS), abi=BaklavaClient.ROUTER_ABI)

    # Utilities
    # -----------------------------------------------------------
    def _is_approved(self, token, amount=MAX_APPROVAL_INT):
        erc20_contract = self.conn.eth.contract(
            address=Web3.toChecksumAddress(token), abi=BaklavaClient.PAIR_ABI)
        print(erc20_contract, token)
        approved_amount = erc20_contract.functions.allowance(self.address, self.router.address).call()
        return approved_amount >= amount

    def is_approved(self, token, amount=MAX_APPROVAL_INT):
        return self._is_approved(token, amount)

    def approve(self, token, max_approval=MAX_APPROVAL_INT):
        if self._is_approved(token, max_approval):
            return

        print("Approving {} of {}".format(max_approval, token))
        erc20_contract = self.conn.eth.contract(
            address=Web3.toChecksumAddress(token), abi=BaklavaClient.ERC20_ABI)

        func = erc20_contract.functions.approve(self.router.address, max_approval)
        params = self._create_transaction_params()
        tx = self._send_transaction(func, params)

        # wait for transaction receipt
        self.conn.eth.waitForTransactionReceipt(tx, timeout=6000)  # TODO raise exception on timeout