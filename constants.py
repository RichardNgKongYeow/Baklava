import os
import json

# Web3 Connect
avax_url="https://api.avax-test.network/ext/bc/C/rpc"
wallet_address = "0x6Ec43b644cD769a1c7695069804E67b2B691e36d"

# Baklava client
synthetic_pool_address="0xdCE353cf62250B94C80F8eD70FFe5fF95304226f"
ABI_synthetic_pool = json.load(open(os.getcwd()+'/BaklavaClient/assets/'+'SyntheticPool.json'))["abi"]

pair_info = {
    0:{
        "pair":"TSLA:USDT",
        "address":"0xfA0d3DDbcfe67D66d8BAA7f963ccDd5551ee19Bf",
        "chain_id":"tsla"
        },
    1:{
        "pair":"AAPL:USDT",
        "address":"0x01a98b5eF7D34b5e60dbF89cff73b6f6aE5162DD",
        "chain_id":"aapl"
    },
    2:{
        "pair":"BTC:USDT",
        "address":"0x33a922c23Fe61b6D05AC2De88b7714809c0faD44",
        "chain_id":"btc"
    },
    # 3:{
    #     "pair":"NFLX:USDT",
    #     "address":"",
    #     "chain_id":"nflx"
    # },
    # 4:{
    #     "pair":"GOOG:USDT",
    #     "address":"",
    #     "chain_id":"goog"
    # },
    # 5:{
    #     "pair":"FB:USDT",
    #     "address":"",
    #     "chain_id":"fb"
    # },
    # 6:{
    #     "pair":"AMZN:USDT",
    #     "address":"",
    #     "chain_id":"amzn"
    # },
    # 7:{
    #     "pair":"SPY:USDT",
    #     "address":"",
    #     "chain_id":"spy"
    # },
    # 8:{
    #     "pair":"IWM:USDT",
    #     "address":"",
    #     "chain_id":"iwm"
    # },
    # 9:{
    #     "pair":"TQQQ:USDT",
    #     "address":"",
    #     "chain_id":"tqqq"
    # },
    # 10:{
    #     "pair":"FX:USDT",
    #     "address":"",
    #     "chain_id":"tqqq"
    # }



}