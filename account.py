import grpcClient
import logging
from BaklavaClient.Wrapper import BaklavaClient
import time



def initialize_logging():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s')
    logging.root.setLevel(logging.INFO)


        

def main():
        initialize_logging()
        grpc = grpcClient
        account = grpc.init_wallet()
        client_list = grpc.init_all_clients(grpc.chain_ids)
        
        while True:
                all_open_positions = query_all_open_long_positions_amounts(account,client_list,grpc)
                print(all_open_positions)
                time.sleep(5)

if __name__ == "__main__":
    main()