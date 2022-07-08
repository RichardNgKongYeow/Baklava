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
    asyncio.ensure_future(process_oo_queue(client))
    asyncio.ensure_future(process_co_queue(client))

    # asyncio.get_event_loop().run_forever(client.run_oo_co_listeners())
    # f1,f2 = await client.run_oo_co_listeners()
    # f1_result = f1.result()
    # print(f1_result)

async def process_oo_queue(client: BaklavaClient):
    while True:
        pair_id, direction, price, base_quantity, order_id  = await client._oo_queue.get()
        print("got item from oo_queue")
        return pair_id, direction, price, base_quantity, order_id

async def process_co_queue(client: BaklavaClient):
    while True:
        pair_id, direction, price, base_quantity, order_id  = await client._co_queue.get()
        print("got item from co_queue")
        return pair_id, direction, price, base_quantity, order_id


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        pass
    finally:
        loop.close()