from dotenv import load_dotenv
import asyncio
import Clients
import time
import logging
import traceback


def run_forever(program):
    
    def wrapper(*args,**kwargs):
        while True:
            try:

                
                # raise Exception("Error simulated!")

                return program(*args,**kwargs)
            except Exception as e:
                print(e, "Something crashed your program. Let's restart it")
                logging.error(f'Error sending transaction {traceback.format_exc()}')
                
                # run_forever(program) # Careful.. recursive behavior
                # Recommended to do this instead
                handle_exception()
    return wrapper

def handle_exception():
    time.sleep(2)
    # code here
    pass




@run_forever
def main():



    # initialise configs and logging
    configs = Clients.initialise_configs()
    Clients.initialise_logging(configs['baklava_client_logs_file'])
    load_dotenv()


    
    # initialise clients
    baklava_client = Clients.initialise_baklava_client(configs)
    client_list = Clients.initialise_marginx_client(configs)

    # # test TODO toggle off
    # x=1/0
    loop = asyncio.get_event_loop()
    myQueue = asyncio.Queue(loop = loop, maxsize=10)
    try:
        loop.run_until_complete(
            asyncio.gather(
                baklava_client.log_event_listener_loop(baklava_client.create_mst_event_filter(), 2,myQueue),
                baklava_client.log_event_listener_loop(baklava_client.create_bst_event_filter(), 2,myQueue),
                Clients.marginx_log_event_executer_loop(client_list,2,myQueue),
                ))
        
        

    finally:

        loop.close()


if __name__ == "__main__":
    # try:
    #     # Create infinite loop to simulate whatever is running
    #     # in your program
    #     while True:
    #         main()
    #         print("Program Running!")
    #         time.sleep(5)

    #         # Simulate an exception which would crash your program
    #         # if you don't handle it!
    #         # raise Exception("Error simulated!")
    # except Exception as e:
    #     print(e, "Something crashed your program. Let's restart it")
    main()