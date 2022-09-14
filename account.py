import MarginX
import logging
from BaklavaClient.Wrapper import BaklavaClient
import time
from dotenv import load_dotenv
import constants
import os


def initialize_logging():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s')
    logging.root.setLevel(logging.INFO)


        

def main():
 # initialize logging
        initialize_logging()

        # initialialise clients
        marginx_account = MarginX.init_wallet(MarginX.seed)
        client_list = MarginX.initialise_all_clients_and_get_all_info(marginx_account,MarginX.chain_ids)
        
        # initialise wrapper
        my_provider = constants.avax_url
        load_dotenv()
        private_key = os.getenv("PRIVATE_KEY")
        address = constants.address

        bclient = BaklavaClient(address, private_key, provider=my_provider)

        while True:
                all_open_positions = MarginX.query_all_open_long_positions_amounts(client_list)
                print("MarginX: {}".format(all_open_positions))

                
                total_supply = bclient.get_syntoken_total_supply()
                print("Baklava: {}".format(total_supply))


                time.sleep(5)

if __name__ == "__main__":
    main()