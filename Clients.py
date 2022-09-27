import logging
import yaml
import os
from BaklavaClient.Wrapper import BaklavaClient





def initialise_configs():
    with open("config.yaml", "r") as ymlfile:
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

        # if client.conn.isConnected() == True:

        #     break
        # return client
# client = initialise_baklava_client(initialise_configs())
# print(client.conn.isConnected())


# def initialise_baklava_client(configs):
#     client_list = initialise_all_baklava_clients(configs)
#     for client in client_list:
#         if client.conn.isConnected() == True:
#             return client
#             break
#         else:




# def initialise_marginx_clients():
#     # initialialise clients
#     marginx_account = MarginX.init_wallet(os.getenv("MARGINX_SEED"))
#     client_list = MarginX.initialise_all_clients_and_get_all_info(marginx_account,constants.pair_info)