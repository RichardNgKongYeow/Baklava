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
        f1,f2 = loop.run_until_complete(client.all())
        print(f1)

    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()