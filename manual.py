import Clients
import logging
from dotenv import load_dotenv
import asyncio


pair_id = "AAPL:USDT"
direction = "MarketBuy"
amount = 73.70
order_id = 0
position = "long"


def initialize_logging():
    logging.basicConfig(filename='manual.csv',level=logging.INFO,format='%(asctime)s,%(levelname)s,%(message)s',datefmt='%m/%d/%Y %I:%M:%S')
    logging.root.setLevel(logging.INFO)



async def main():

    # initialize logging
    initialize_logging()
    load_dotenv()
    configs = Clients.initialise_configs()

    # initialialise clients
    client_dict = Clients.initialise_marginx_client(configs)
    
    await Clients.run_and_log_manual_executor(pair_id, direction, amount, position, client_dict)




if __name__ == "__main__":
    while True:
        asyncio.run(main())