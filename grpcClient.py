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

import logging


chain_ids = ["tsla",
    "aapl",
    "btc",
    "nflx",
    "goog",
    "fb",
    "amzn",
    "spy",
    "iwm",
    "tqqq",
    "fx"
]

pairs={0:"TSLA:USDT", 1:"AAPL:USDT", 2: "BTC:USDT", 3: "NFLX:USDT", 4:"GOOG:USDT", 5: "FB:USDT", 6: "AMZN:USDT", 7: "SPY:USDT", 8: "IWM:USDT", 9: "TQQQ:USDT", 10: "FX:USDT"}


# -------------------------------Init clients-------------------------------------------
# client = GRPCClient("https://testnet-btc-grpc.marginx.io:9090")
def init_GRPCClient(chain_id:str)->object:
    """
    initialiase a client
    """
    try:
        client = GRPCClient(f"https://testnet-{chain_id}-grpc.marginx.io:9090")
        chain_id = client.query_chain_id()
        logging.info('chain_id: {}'.format(chain_id))
        return client
    except Exception as e:
        logging.critical("Unable to initialise client due to error: {} of type {}".format(e,type(e)))


def init_all_clients(chain_ids:list)->list:
    """
    initialiase all clients objected to be executed later and return an array
    of clients
    """
    client_list=[]
    for chain_id in chain_ids:
        client = init_GRPCClient(chain_id)
        client_list.append(client)
    return client_list


def get_client(chain_id:str,client_list:list)->object:
    """
    get clients based on the index from the chain_id array
    """
    try:
        index = chain_ids.index(chain_id)
        return client_list[index]
    except Exception as e:
        logging.error("failed to get client due to error: {} of type {}".format(e,type(e)))

# --------------------------------------utils---------------------------------------------
def convert_to_lower_case(string:str)->str:
    return string.lower()

# --------------------------------------account info--------------------------------------

def init_wallet()->object:
    """
    initialise wallet and return the account object which will later be used for
    TxBuilder
    """
    seed = "gesture surface wave update party conduct husband lab core zone visa body phrase brother water team very cheap suspect sword material page decrease kiwi"

    # Create TxBuilder
    Account.enable_unaudited_hdwallet_features()
    try:
        account = Account.from_mnemonic(seed)
        logging.info('address: {}'.format(account.address))
        return account
    except Exception as e:
        logging.critical("Unable to initialise wallet due to error: {} of type {}".format(e,type(e)))

def get_account_info(client:object, account:object)->object:
    """
    return account_info needed for TxBuilder
    """
    try:
        account_info = client.query_account_info(account.address)
        # logging.info('account number: {}, sequence: {}'.format(account_info.account_number,account_info.sequence))
        return account_info
    except Exception as e:
        logging.error("failed to get account info due to error: {} of type {}".format(e,type(e)))

def get_account_sequence(account_info:object)->int:
    # TODO manually added a 100 to acct sequence to fix immediate error
    """
    return an account sequence int
    """
    try:
        return account_info.sequence
    except Exception as e:
        logging.error("failed to get account sequence due to error: {} of type {}".format(e,type(e)))

# ===================================querying postiions info==============================
#  -----------------------------single chain query----------------------------------------
def query_positions(account:str, client:object, pair_id:str)->list:
        """
        query position of an account given a pair_id and corresponding client
        """
        try:
                positions = client.query_positions(
                        owner=account.address, pair_id=pair_id)
                return positions
        except Exception as e:
                logging.error("unable to query positions due to error: {} of type {}".format(e,type(e)))


def is_empty_array(positions:list)->bool:
        """
        check to see is array is empty, return True is empty
        """
        try:
                if len(positions) == 0:
                        return True
                else:
                        return False
        except Exception as e:
                logging.error("unable to check if array is empty due to error: {} of type {}".format(e,type(e)))



def is_long(position:list)->bool:
        """
        check direction if short or long
        """
        try:
                direction = position[3]
                if direction == 1:
                        return True
                elif direction == 2:
                        return False
                else:
                        pass
        except Exception as e:
                logging.error("unable to check direction due to error: {} of type {}".format(e,type(e)))


def get_open_long_position_amount(positions:list,client:object,pair_id:str)->float:
        """
        get the array of the long position checking to see if array is empty first
        """
        try:
                if is_empty_array(positions) == True:
                        # logging.info("Pair {} has no open positions".format(pair_id))
                        open_position_amount = 0
                else:
                        for position in positions:
                                if is_long(position) == True:
                                        open_position_amount = grpcClient.Decimal(position[7])
                                        logging.info("Pair {} has long position of Amount {}".format(pair_id,open_position_amount))
                                        return open_position_amount
                                else:
                                        open_position_amount = 0
                                        logging.info("Pair {} has short position of Amount {}".format(pair_id,open_position_amount))
                return open_position_amount
                
        except Exception as e:
                logging.error("Can't get open long position amount due to {} of type {}".format(e,type(e)))

def get_open_long_position_amount(open_position)


def query_all_open_long_positions_amounts(account:str,client_list:list,grpc:grpcClient):
        all_open_positions = {}
        for i in range(0,10):
                client = client_list[i]
                pair_id = grpc.pairs[i]
                positions = query_positions(account, client, pair_id)
                open_position_amount = get_open_long_position_amount(positions=positions, client=client,pair_id=pair_id)
                all_open_positions[pair_id] = open_position_amount
        return all_open_positions


# ----------------------------------build mx tx-------------------------------------------
def get_tx_builder(chain_id,account,account_info)->object:
    """
    return Txbuilder object
    """
    try:
        tx_builder = TxBuilder(account, None, chain_id, account_info.account_number, Coin(
        amount='600', denom='USDT'))
        return tx_builder
    except Exception as e:
        logging.error("failed to create tx_builder due to error: {} of type {}".format(e,type(e)))



def build_mx_txbuilder(account,gchain_id,client_list):
    """
    return the necessary building blocks for building the Tx
    """
    client = get_client(gchain_id,client_list)
    chain_id = client.query_chain_id()
    account_info = get_account_info(client,account)
    acc_seq = get_account_sequence(account_info)
    tx_builder = get_tx_builder(chain_id,account,account_info)
    return client, acc_seq, tx_builder


# --------------------------------execute marginx transactions---------------------------
async def execute_mx_tx(account,client_list, pair_id, direction, amt):
    """
    input trade info and execute order on marginX
    """
    chain_id = convert_to_lower_case(pair_id.split(":")[0])
    client, acc_seq, tx_builder = build_mx_txbuilder(account, chain_id, client_list)
    
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
            base_quantity=Decimal(amt*10**-3),
            leverage=5,
            acc_seq=acc_seq,
            mode=BROADCAST_MODE_BLOCK,
        )

        # order_id = None
        events = json.loads(tx_response.raw_log)[0]['events']
        return events

    except Exception as e:
        logging.error("marginx tx failed: {} of type {}".format(e,type(e)))
        
async def close_mx_tx(self, pair_id, direction, amt, grpc: grpcClient):
    chain_id = grpc.convert_to_lower_case(pair_id.split(":")[0])
    client, acc_seq, tx_builder = self.build_mx_txbuilder(chain_id, grpc)

    client.close_position(tx_builder, pair_id, positions[0].Id, grpc.decimal.Decimal(amt), grpc.decimal.Decimal(
        0.1), True, acc_seq, True, mode=grpc.BROADCAST_MODE_BLOCK)


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

