import yaml
from web3 import Web3
from dotenv import load_dotenv
from Configs import Pairs
import os
import time
import asyncio
import Clients





async def main():

    pairs = Clients.update_pairs_configs()
    # print(pairs)



if __name__ == "__main__":     
    asyncio.run(main())