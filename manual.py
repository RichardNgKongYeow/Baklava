import Clients
import logging
from dotenv import load_dotenv
import asyncio


pair_id = "ETH:USDT"
direction = "MarketSell"
amount = 5
order_id = 0
position = "long"


def initialize_logging(filename):
    logging.basicConfig(filename=filename,level=logging.INFO,format='%(asctime)s,%(levelname)s,%(message)s',datefmt='%m/%d/%Y %I:%M:%S')
    logging.root.setLevel(logging.INFO)



async def main():

    # initialize logging

    load_dotenv()
    configs = Clients.initialise_configs()
    initialize_logging(configs['manual_client_logs_files'])

    # initialialise clients
    client_dict = Clients.initialise_marginx_client(configs)
    
    await Clients.run_and_log_manual_executor(pair_id, direction, amount, position, client_dict)




if __name__ == "__main__":
    asyncio.run(main())