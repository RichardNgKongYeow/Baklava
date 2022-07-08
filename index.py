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
    client

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(client.all())
        
        

    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()