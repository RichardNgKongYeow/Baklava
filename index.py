from dotenv import load_dotenv
import asyncio
import Clients







def main():

    # initialise configs and logging
    configs = Clients.initialise_configs()
    Clients.initialise_logging(configs['baklava_client_logs_file'])
    load_dotenv()


    
    # initialise clients
    baklava_client = Clients.initialise_baklava_client(configs)
    client_list = Clients.initialise_marginx_client(configs)


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
    main()