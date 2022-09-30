import logging
import yaml
import os
from BaklavaClient.Wrapper import BaklavaClient
from Marginx import MarginX
import asyncio




def initialise_configs():
    full_path = os.getcwd()
    with open(full_path+"/Configs/config.yaml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        return cfg[cfg['environment']]


def initialise_logging(filename):
    logging.basicConfig(filename=filename,level=logging.INFO,format='%(asctime)s,%(levelname)s,%(message)s',datefmt='%m/%d/%Y %I:%M:%S')



def initialise_baklava_client(configs):
    private_key = os.getenv("PRIVATE_KEY")
    # loop through range of no of web3 urls and initialise BaklavaClient
    for i in range(1,5):
        client = BaklavaClient(configs, private_key, provider=configs['web3_url'][i])
        if client.conn.isConnected() == True:
            break
    return client



def initialise_marginx_client(configs):
    marginx_account = MarginX.init_wallet(os.getenv("MARGINX_SEED"))
    client_list = MarginX.initialise_all_clients_and_get_all_info(marginx_account,configs)
    return client_list


async def marginx_log_event_executer_loop(client_list, poll_interval, myQueue):
    await asyncio.wait([MarginX.get_item_from_queue_and_execute(client_list,1,myQueue),MarginX.get_item_from_queue_and_execute(client_list,2,myQueue)])
    await asyncio.sleep(poll_interval)