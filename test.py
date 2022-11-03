import yaml
from web3 import Web3
import Clients
from dotenv import load_dotenv
from Configs import Pairs
from Marginx.grpcClient import grpcClient
from Marginx import MarginX
import os
import time
import asyncio

chain_id = "eth"
load_dotenv()
# print(os.getenv("MARGINX_SEED"))
marginx_account = MarginX.init_wallet(os.getenv("MARGINX_SEED"))
configs = Clients.initialise_configs()

client = grpcClient(marginx_account,chain_id,configs)
client.initialise_client_and_get_all_info()
# print(client.account_info)

async def open_position():
    print(client.pair_id,client.marginx_chain_id,client.account_info)
    open_position = await client.query_open_positions()
    return open_position



async def main():
    while True:
        position = await open_position()
        print(position)
        time.sleep(20)


if __name__ == "__main__":     # __name__ is a built-in variable in Python which evaluates to the name of the current module.
    asyncio.run(main())