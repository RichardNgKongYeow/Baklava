from web3 import Web3

def convert_to_lower_case(string:str)->str:
    return string.lower()

def convert_pair_id_to_chain_id(pair_id:str)->str:
    chain_id = convert_to_lower_case(pair_id.split(":")[0])
    return chain_id


def fromWei(value):
    return Web3.fromWei(value, 'ether')

def from3dp(value):
    return value * 10**(-3)

def to3dp(value):
    return value * 10**(3)