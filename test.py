import yaml
from web3 import Web3
from dotenv import load_dotenv
from Configs import Pairs
import os
import time
import asyncio
import Clients
from Marginx.grpcClient import grpcClient
from Marginx import MarginX
from Helpers.Loggers import Logger




async def main():

    # logging.basicConfig(filename="systems_log.log",level=logging.INFO,format='%(asctime)s,%(levelname)s,%(message)s',datefmt='%m/%d/%Y %I:%M:%S')
    # load_dotenv()
    # configs = Clients.initialise_configs()
    # marginx_account = MarginX.init_wallet(os.getenv("MARGINX_SEED"))
    # MarginX.init_wallet(marginx_account)
    # pairs = Clients.update_pairs_configs()
    # client = grpcClient(account = marginx_account,chain_id="tsla",configs = configs)
    # client.initialise_client_and_get_all_info()
    







if __name__ == "__main__":     
    asyncio.run(main())