from venv import create
from BaklavaClient.Wrapper import SynTClient
import constants
from web3 import Web3
from dotenv import load_dotenv
import os
import asyncio
import logging
import MarginX
import time


my_provider = constants.avax_url
load_dotenv()
private_key = os.getenv("PRIVATE_KEY")


def create_client_list():

    syntetic_tokens = {"bTSLA":"0x0D95b3f47606339FE7055938e1fACc457177aE21","bAAPL":"0x9BD0E966D7457810862E57c8F1e36a1c331fEca0","bBTC":"0xA2c2c0686FabEd8186E29CeBeB7cccBC416cb03D"}
    client_list = {}

    for i in syntetic_tokens:
        # print(syntetic_tokens[i])
        client = SynTClient(syntetic_tokens[i],private_key, provider=my_provider)
        client_list[i] = client
    print(client_list)
    return client_list

def get_total_supply():
    client_list = create_client_list()
    total_supplies=[]
    for i in client_list:
        total_supply = i.get_total_supply()
        total_supplies.append(total_supply)
    print(total_supplies)




def main():
    while True:
        # get_total_supply()
        create_client_list()
        time.sleep(5)

if __name__ == "__main__":
    main()