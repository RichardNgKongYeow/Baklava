import logging
import yaml
import os
from BaklavaClient.Wrapper import BaklavaClient
from Marginx import MarginX
import asyncio
from Configs import Pairs
import ruamel.yaml
# from Helpers.Utils import exception_logger
import Helpers.Utils as Utils
from Helpers.Loggers import Logger




def initialise_configs():
    full_path = os.getcwd()
    with open(full_path+"/Configs/config.yaml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        return cfg[cfg['environment']]


# # TODO remove?
def initialise_system_logger(configs):
    system_logger = Logger(configs["logs"]["logger_name"]["system"],configs["logs"]["logs_file_name"]["system"])
    return system_logger

def initialise_tx_logger(configs):
    tx_logger = Logger(configs["logs"]["logger_name"]["tx"],configs["logs"]["logs_file_name"]["tx"])
    return tx_logger




def initialise_baklava_client(configs,system_logger, tx_logger):
    private_key = os.getenv("PRIVATE_KEY")
    # loop through range of no of web3 urls and initialise BaklavaClient
    for i in range(1,6):
        client = BaklavaClient(configs, private_key, system_logger, tx_logger, provider=configs['web3_url'][i])
        if client.conn.isConnected() == True:
            break
    return client



def initialise_marginx_client(configs,system_logger, tx_logger):
    marginx_account = MarginX.init_wallet(os.getenv("MARGINX_SEED"))
    client_list = MarginX.initialise_all_clients_and_get_all_info(marginx_account,configs,system_logger, tx_logger)
    return client_list


async def marginx_log_event_executer_loop(client_list, poll_interval, myQueue):
    await asyncio.wait([MarginX.get_item_from_queue_and_execute(client_list,1,myQueue),MarginX.get_item_from_queue_and_execute(client_list,2,myQueue)])
    await asyncio.sleep(poll_interval)



async def manual_executor(pair_id, direction, amount, position, client_dict):
    
    CLIENT_NAME = "ManualExecutor"

    client = MarginX.get_client(pair_id, client_dict)

    # manipulate amount
    amount = Utils.mulby10power3(amount)

    if position == "short":
        if direction == "MarketBuy":
            tx_func = await client.open_long_position(direction, amount)
            tx_response = await client._send_tx(tx_func)
        elif direction == "MarketSell":
            tx_func = await client.close_open_long_position(amount)
            tx_response = await client._send_tx(tx_func)
    elif position == "long":
        if direction == "MarketBuy":
            tx_func = await client.open_long_position(direction, amount)
            tx_response = await client._send_tx(tx_func)
        elif direction == "MarketSell":
            tx_func = await client.close_open_long_position(amount)
            tx_response = await client._send_tx(tx_func)
    await client.log_order_info(tx_response)
    



async def run_and_log_manual_executor(pair_id, direction, amount, position, client_dict):
    client = MarginX.get_client(pair_id, client_dict)
    events = await manual_executor(pair_id, direction, amount, position, client_dict)
    # await client.log_order_info(events)


def get_pairs_mapping():
    pairs = {}
    configs = initialise_configs()
    for chain_id in Pairs.chain_ids:
        pairs[configs["chain_id"][chain_id]["index"]] = configs["chain_id"][chain_id]["pair_id"]

    return pairs

# TODO stopped here 
def update_pairs_configs():
    full_path = os.getcwd()
    file_name = '/Configs/config.yaml'
    # with open(full_path+"/Configs/config.yaml", "r") as ymlfile:
    #     configs = yaml.load(ymlfile, Loader=yaml.FullLoader)

    config, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(open(full_path+file_name))
    config[config["environment"]]["pairs"] = get_pairs_mapping()


    # # print(configs)

    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=ind, sequence=ind, offset=bsi) 

    with open(full_path+"/Configs/config.yaml", "w") as fp:
        yaml.dump(config,fp)
        