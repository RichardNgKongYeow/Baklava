import grpcClient


# print(grpcClient.client.query_account_info(grpcClient.account.address))

positions = grpcClient.client.query_positions(
            owner='0x1056C9e553587AC23d3d54C8b1C2299Dd4093C72', pair_id="BTC:USDT")


account_info = grpcClient.client.query_account_info(grpcClient.account.address)
account_balance = grpcClient.client.query_all_balances(address=grpcClient.account.address)
balance = grpcClient.client.query_balance(address=grpcClient.account.address, denom="FX")
print("positions: ", positions)
print(balance)
print(account_balance)
print('account number:', account_info.account_number,
        'sequence:', account_info.sequence)