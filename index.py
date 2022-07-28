from BaklavaClient.Wrapper import BaklavaClient
import constants
from web3 import Web3
from dotenv import load_dotenv
import os
import asyncio
import grpcClient


def main():

    # initialialise clients
    client_list = grpcClient.init_all_clients(grpcClient.chain_ids)
    marginx_account = grpcClient.init_wallet()


    my_provider = constants.avax_url
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    address = constants.address

    client = BaklavaClient(address, private_key, marginx_account, client_list, provider=my_provider)

    loop = asyncio.get_event_loop()
    myQueue = asyncio.Queue(loop = loop, maxsize=10)
    try:
        loop.run_until_complete(
            asyncio.gather(
                client.log_loop(client.create_mst_event_filter(), 2,myQueue),
                client.log_loop(client.create_bst_event_filter(), 2,myQueue)
                
                ))

    finally:

        loop.close()


if __name__ == "__main__":
    main()