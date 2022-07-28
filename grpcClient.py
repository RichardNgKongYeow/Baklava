from itertools import chain
from subprocess import list2cmdline
from turtle import position
import unittest

from eth_account import Account

from fx_py_sdk import wallet
from fx_py_sdk.grpc_client import GRPCClient
# from fx_py_sdk.fx_rpc.rpc import HttpRpcClient
from fx_py_sdk.builder import TxBuilder
from fx_py_sdk.codec.cosmos.base.v1beta1.coin_pb2 import Coin
from fx_py_sdk.codec.fx.dex.v1.order_pb2 import *
import decimal
from fx_py_sdk.codec.cosmos.tx.v1beta1.service_pb2 import BROADCAST_MODE_BLOCK, BROADCAST_MODE_SYNC
from google.protobuf.json_format import MessageToJson
import json

from fx_py_sdk.ibc_transfer import ConfigsKeys, Ibc_transfer

chain_ids = ["aapl",
# "amzn",
# "btc",
# "fb",
# "fx",
# "goog",
# "iwm",
# "nflx",
# "spy",
# "tqqq",
"tsla"
]



# client = GRPCClient("https://testnet-btc-grpc.marginx.io:9090")
def init_GRPCClient(chain_id:str)->object:
    """
    initialiase a client
    """
    return GRPCClient(f"https://testnet-{chain_id}-grpc.marginx.io:9090")


def convert_to_lower_case(string:str)->str:
    return string.lower()

def init_all_clients(chain_ids:list)->list:
    """
    initialiase all clients objected to be executed later and return an array
    of clients
    """
    client_list=[]
    for chain_id in chain_ids:
        client = init_GRPCClient(chain_id)
        chain_id = client.query_chain_id()
        print('chain_id:', chain_id)
        client_list.append(client)
    return client_list



def get_client(chain_id:str,client_list:list)->object:
    """
    get clients based on the index from the chain_id array
    """
    index = chain_ids.index(chain_id)
    return client_list[index]

def init_wallet()->object:
    """
    initialise wallet and return the account object which will later be used for
    TxBuilder
    """
    seed = "gesture surface wave update party conduct husband lab core zone visa body phrase brother water team very cheap suspect sword material page decrease kiwi"

    # Create TxBuilder
    Account.enable_unaudited_hdwallet_features()
    account = Account.from_mnemonic(seed)
    print('address: ', account.address)
    return account

def get_account_info(client:object, account:object)->object:
    """
    return account_info needed for TxBuilder
    """
    account_info = client.query_account_info(account.address)
    print('account number:', account_info.account_number,
            'sequence:', account_info.sequence)
    return account_info

def get_tx_builder(chain_id,account,account_info)->object:
    """
    return Txbuilder object
    """
    tx_builder = TxBuilder(account, None, chain_id, account_info.account_number, Coin(
        amount='600', denom='USDT'))
    return tx_builder

def get_account_sequence(account_info:object)->int:
    # TODO manually added a 100 to acct sequence to fix immediate error
    """
    return an account sequence int
    """
    return account_info.sequence



from decimal import Decimal
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

