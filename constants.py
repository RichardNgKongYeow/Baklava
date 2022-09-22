import os
import json

# Web3 Connect
avax_url="https://api.avax-test.network/ext/bc/C/rpc"
wallet_address = "0x6Ec43b644cD769a1c7695069804E67b2B691e36d"

# Baklava client
synthetic_pool_address="0x1f2A2A8eBF8Ec7102Bf15cb6eC5629A9E05b410a"
ABI_synthetic_pool = json.load(open(os.getcwd()+'/BaklavaClient/assets/'+'SyntheticPool.json'))["abi"]

pair_info = {
    0:{
        "pair":"TSLA:USDT",
        "address":"0x0D95b3f47606339FE7055938e1fACc457177aE21",
        "chain_id":"tsla"
        },
    1:{
        "pair":"AAPL:USDT",
        "address":"0x9BD0E966D7457810862E57c8F1e36a1c331fEca0",
        "chain_id":"aapl"
    },
    2:{
        "pair":"BTC:USDT",
        "address":"0xA2c2c0686FabEd8186E29CeBeB7cccBC416cb03D",
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