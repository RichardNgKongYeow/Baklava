from BaklavaClient.Wrapper import BaklavaClient
import constants
from web3 import Web3
from dotenv import load_dotenv
import os
import asyncio



async def main():

    my_provider = constants.avax_url
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    address = constants.address

    client = BaklavaClient(address, private_key, provider=my_provider)
    f1 = loop.create_task(client.log_loop(client.create_oo_event_filter(), 2))
    f2 = loop.create_task(client.log_loop(client.create_co_event_filter(), 2))
    await asyncio.wait([f1,f2])
    return f1,f2
    


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        d1,d2 = loop.run_until_complete(main())
        print(d1.result())
    except Exception as e:
        pass
    finally:
        loop.close()