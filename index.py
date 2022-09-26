from BaklavaClient.Wrapper import BaklavaClient
from dotenv import load_dotenv
import os
import asyncio
import logging
import MarginX






def main():

    # initialize logging
    initialise_logging()
    load_dotenv()


    

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