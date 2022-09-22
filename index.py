from BaklavaClient.Wrapper import BaklavaClient
import constants
from web3 import Web3
from dotenv import load_dotenv
import os
import asyncio
import logging
import MarginX
import threading
import Monitor



def initialize_logging():
    logging.basicConfig(filename='logs.csv',level=logging.INFO,format='%(asctime)s,%(levelname)s,%(message)s',datefmt='%m/%d/%Y %I:%M:%S')
    logging.root.setLevel(logging.INFO)


def main():

    # initialize logging
    initialize_logging()
    load_dotenv()

    # initialialise clients
    marginx_account = MarginX.init_wallet(os.getenv("MARGINX_SEED"))
    client_list = MarginX.initialise_all_clients_and_get_all_info(marginx_account,constants.pair_info)
    

    # initialise Baklava client
    my_provider = constants.avax_url
    private_key = os.getenv("PRIVATE_KEY")
    address = constants.wallet_address
    client = BaklavaClient(address, private_key, provider=my_provider)


    loop = asyncio.get_event_loop()
    myQueue = asyncio.Queue(loop = loop, maxsize=10)
    try:
        loop.run_until_complete(
            asyncio.gather(
                client.log_event_listener_loop(client.create_mst_event_filter(), 2,myQueue),
                client.log_event_listener_loop(client.create_bst_event_filter(), 2,myQueue),
                MarginX.log_event_executer_loop(client_list,2,myQueue),
                ))
        
        

    finally:

        loop.close()


if __name__ == "__main__":
    main()