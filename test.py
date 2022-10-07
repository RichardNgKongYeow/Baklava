import yaml
from web3 import Web3
import Clients
from dotenv import load_dotenv
from Configs import Pairs
from Marginx.grpcClient import grpcClient
from Marginx import MarginX
import os
import time

chain_id = "tsla"
load_dotenv()
# print(os.getenv("MARGINX_SEED"))
marginx_account = MarginX.init_wallet(os.getenv("MARGINX_SEED"))
configs = Clients.initialise_configs()

client = grpcClient(marginx_account,chain_id,configs)
client.initialise_client_and_get_all_info()
# print(client.account_info)

while True:
    print(client.query_open_positions())
    time.sleep(20)