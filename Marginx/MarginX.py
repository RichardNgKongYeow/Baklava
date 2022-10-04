from Marginx.grpcClient import grpcClient
import logging
from eth_account import Account
from Configs import Pairs




def initialise_all_clients_and_get_all_info(account:object,configs:dict)->list:
    """
    initialiase all clients objected to be executed later and return an array
    of clients
    """
    client_dict={}
    for chain_id in Pairs.chain_ids:
        pair = configs['chain_id'][chain_id]['pair_id']
        client = grpcClient(account,chain_id, configs)
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
            events = await client.open_long_position(direction, amount)
        elif direction == "MarketSell":
            events = await client.close_open_long_position(amount)
        await client.log_order_info(events)


