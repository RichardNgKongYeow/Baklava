import MarginX
import logging
from dotenv import load_dotenv
import constants
import os
import asyncio

pair_id = "AAPL:USDT"
direction = "MarketBuy"
amount = 0.67
order_id = 0


def initialize_logging():
    logging.basicConfig(filename='manual.csv',level=logging.INFO,format='%(asctime)s,%(levelname)s,%(message)s',datefmt='%m/%d/%Y %I:%M:%S')
    logging.root.setLevel(logging.INFO)



def main():

    # initialize logging
    initialize_logging()
    load_dotenv()

    # initialialise clients
    marginx_account = MarginX.init_wallet(os.getenv("MARGINX_SEED"))
    client_list = MarginX.initialise_all_clients_and_get_all_info(marginx_account,constants.pair_info)
    
    
    loop = asyncio.get_event_loop()
    myQueue = asyncio.Queue(loop = loop, maxsize=10)

    try:
        loop.run_until_complete(
            asyncio.gather(
                myQueue.put((pair_id, direction, amount, order_id)),
                MarginX.log_event_executer_loop(client_list,2,myQueue)))
    
    finally:

        loop.close()



if __name__ == "__main__":
    main()