import yaml
from web3 import Web3
import Clients

configs = Clients.initialise_configs()

for i in range(1,5):
    if Web3(Web3.HTTPProvider(configs['web3_url'][i])).isConnected() == True:
        print (configs['web3_url'][i])
        break
        

