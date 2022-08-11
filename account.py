import grpcClient
import logging
from BaklavaClient.Wrapper import BaklavaClient
import time



def initialize_logging():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s')
    logging.root.setLevel(logging.INFO)

#  -----------------------------single chain query----------------------------------------
def query_positions(account:str, client:object, pair_id:str)->list:
        """
        query position of an account given a pair_id and corresponding client
        """
        try:
                positions = client.query_positions(
                        owner=account.address, pair_id=pair_id)
                return positions
        except Exception as e:
                logging.error("unable to query positions due to error: {} of type {}".format(e,type(e)))


def is_empty_array(positions:list)->bool:
        """
        check to see is array is empty, return True is empty
        """
        try:
                if len(positions) == 0:
                        return True
                else:
                        return False
        except Exception as e:
                logging.error("unable to check if array is empty due to error: {} of type {}".format(e,type(e)))



def is_long(position:list)->bool:
        """
        check direction if short or long
        """
        try:
                direction = position[3]
                if direction == 1:
                        return True
                elif direction == 2:
                        return False
                else:
                        pass
        except Exception as e:
                logging.error("unable to check direction due to error: {} of type {}".format(e,type(e)))


def get_open_long_position_amount(positions:list,client:object,pair_id:str)->float:
        """
        get the array of the long position checking to see if array is empty first
        """
        try:
                if is_empty_array(positions) == True:
                        logging.info("Pair {} has no open positions".format(pair_id))
                        open_position_amount = 0
                else:
                        for position in positions:
                                if is_long(position) == True:
                                        open_position_amount = grpcClient.Decimal(position[7])
                                        logging.info("Pair {} has long position of Amount {}".format(pair_id,open_position_amount))
                                        return open_position_amount
                                else:
                                        open_position_amount = 0
                                        logging.info("Pair {} has short position of Amount {}".format(pair_id,open_position_amount))
                return open_position_amount
                
        except Exception as e:
                logging.error("Can't get open long position amount due to {} of type {}".format(e,type(e)))



def query_all_open_long_positions_amounts(account:str,client_list:list,grpc:grpcClient):
        all_open_positions = {}
        for i in range(0,10):
                client = client_list[i]
                pair_id = grpc.pairs[i]
                positions = query_positions(account, client, pair_id)
                open_position_amount = get_open_long_position_amount(positions=positions, client=client,pair_id=pair_id)
                all_open_positions[pair_id] = open_position_amount
        return all_open_positions
        

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