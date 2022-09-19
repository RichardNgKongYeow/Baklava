from grpcClient import grpcClient
import logging
from eth_account import Account
import utils
import asyncio
import constants


seed = "gesture surface wave update party conduct husband lab core zone visa body phrase brother water team very cheap suspect sword material page decrease kiwi"


def initialise_all_clients_and_get_all_info(account:object,pair_info:dict)->list:
    """
    initialiase all clients objected to be executed later and return an array
    of clients
    """
    client_dict={}
    for i in pair_info:
        pair = pair_info[i]['pair']
        client = grpcClient(account,i)
        client.initialise_client_and_get_all_info()
        client_dict[pair] = client
    return client_dict

def get_client(pair_id:str,client_dict:dict)->object:
    """
    get clients based on the index from the chain_id array
    """
    try:
        return client_dict[pair_id]
    except Exception as e:
        logging.error("failed to get client due to error: {} of type {}".format(e,type(e)))

def init_wallet(seed)->object:
    """
    initialise wallet and return the account object which will later be used for
    TxBuilder
    """
    # Create TxBuilder
    Account.enable_unaudited_hdwallet_features()
    try:
        account = Account.from_mnemonic(seed)
        logging.info('address: {}'.format(account.address))
        return account
    except Exception as e:
        logging.critical("Unable to initialise wallet due to error: {} of type {}".format(e,type(e)))


def query_all_open_long_positions_amounts(client_dict:dict)->dict:
    """
    query and return a dict of open position amount eg.

    {"BTC:USDT":50}
    """
    
    all_open_positions = {}
    for i in client_dict.values():
        client = i
        pair_id = client.pair_id
        open_position_amount = client.get_open_long_position_amount()
        all_open_positions[pair_id] = open_position_amount
    return all_open_positions


# -----------------------------------queue system-------------------------------------
async def get_item_from_queue_and_execute(client_dict,id,myQueue):
    while True:
        print("Consumer: {} attempting to get from queue".format(id))
        pair_id, direction, amount, order_id = await myQueue.get()
        client = get_client(pair_id, client_dict)
        if direction == "MarketBuy":
            events = await client.open_long_mx_position(direction, amount)
        else:
            events = await client.close_long_open_position(amount)
        await client.log_order_info(events)


async def log_event_executer_loop(client_list, poll_interval, myQueue):
    await asyncio.wait([get_item_from_queue_and_execute(client_list,1,myQueue),get_item_from_queue_and_execute(client_list,2,myQueue)])
    await asyncio.sleep(poll_interval)