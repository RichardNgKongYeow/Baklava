from BaklavaClient.Wrapper import BaklavaClient
import constants
from web3 import Web3
from dotenv import load_dotenv
import os
import asyncio



def main():

    my_provider = constants.avax_url
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    address = constants.address

    client = BaklavaClient(address, private_key, provider=my_provider)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                client.log_loop(client.create_mst_event_filter(), 2),
                client.log_loop(client.create_bst_event_filter(), 2)
                
                ))

                # log_loop(block_filter, 2),
                # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()