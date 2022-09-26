import logging
import yaml
import os
from BaklavaClient.Wrapper import BaklavaClient


pairs=[
    "tsla",
    "aapl",
    "btc",
    # "nflx",
    # "goog",
    # "fb",
    # "amzn",
    # "spy",
    # "iwm",
    # "tqqq",
    # "fx"
]


def initialise_configs():
    with open("config.yaml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        return cfg[cfg['environment']]


def initialise_logging(filename):
    logging.basicConfig(filename=filename,level=logging.INFO,format='%(asctime)s,%(levelname)s,%(message)s',datefmt='%m/%d/%Y %I:%M:%S')
    logging.root.setLevel(logging.INFO)

print(initialise_configs()['web3_url'])

def initialise_baklava_client(configs):-
    pai
    my_provider = configs['web3_url']
    private_key = os.getenv("PRIVATE_KEY")
    client = BaklavaClient(configs, private_key, provider=my_provider)
    return client


# def initialise_marginx_clients():
#     # initialialise clients
#     marginx_account = MarginX.init_wallet(os.getenv("MARGINX_SEED"))
#     client_list = MarginX.initialise_all_clients_and_get_all_info(marginx_account,constants.pair_info)