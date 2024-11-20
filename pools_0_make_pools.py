from web3 import Web3, HTTPProvider
from utils import eth_node_url, read_json_file, write_json_file
import json

web3 = Web3(HTTPProvider(eth_node_url))
factory_address_v2 = Web3.to_checksum_address('0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f')  
factory_abi_v2 = json.load(open('./abis/UniswapV2Factory.json'))  
factory_contract_v2 = web3.eth.contract(address=factory_address_v2, abi=factory_abi_v2)

factory_address_v3 = Web3.to_checksum_address('0x1F98431c8aD98523631AE4a59f267346ea31F984')  
factory_abi_v3 = json.load(open('./abis/UniswapV3Factory.json'))  
factory_contract_v3 = web3.eth.contract(address=factory_address_v3, abi=factory_abi_v3)

def get_v2_pool_address(tokenA, tokenB):
    try:
        pool_address = factory_contract_v2.functions.getPair(
            Web3.to_checksum_address(tokenA), 
            Web3.to_checksum_address(tokenB)
        ).call()

        if pool_address != '0x0000000000000000000000000000000000000000':
            return pool_address
        else:
            return None
    except Exception as e:
        print(f"Error fetching pool for {tokenA} and {tokenB}: {e}")
        return None

def get_v3_pool_address(tokenA, tokenB, fee):
    try:
        pool_address = factory_contract_v3.functions.getPool(
            Web3.to_checksum_address(tokenA), 
            Web3.to_checksum_address(tokenB),
            fee
        ).call()

        if pool_address != '0x0000000000000000000000000000000000000000':
            return pool_address
        else:
            return None
    except Exception as e:
        print(f"Error fetching V3 pool for {tokenA} and {tokenB} with fee {fee}: {e}")
        return None
    
tokens = read_json_file('./data/', 'ERC20_tokens.json')
found_pools_v2 = []

for i in range(len(tokens)):
    for j in range(i + 1, len(tokens)):
        tokenA = tokens[i]
        tokenB = tokens[j]
        
        print(f"Checking pool for {tokenA['symbol']} and {tokenB['symbol']}...")
        
        pool_address = get_v2_pool_address(tokenA['address'], tokenB['address'])
        
        if pool_address:
            pool_info = {
                "tokenA": tokenA["symbol"],
                "tokenB": tokenB["symbol"],
                "tokenA_address": tokenA["address"],
                "tokenB_address": tokenB["address"],
                "pool_address": pool_address
            }
            found_pools_v2.append(pool_info)
            write_json_file('./data/', 'found_pools_v2.json', found_pools_v2)
            print(f"Found pool for {tokenA['symbol']} and {tokenB['symbol']}: {pool_address}")
        else:
            print(f"No pool found for {tokenA['symbol']} and {tokenB['symbol']}.")
            
found_pools_v3 = []
v3_fee_tiers = [3000] # Possible also: [500, 3000, 10000] (0.05%, 0.3%, 1%)

for i in range(len(tokens)):
    for j in range(i + 1, len(tokens)): 
        tokenA = tokens[i]
        tokenB = tokens[j]
        
        for fee in v3_fee_tiers:
            print(f"Checking Uniswap V3 pool for {tokenA['symbol']} and {tokenB['symbol']} with fee {fee / 10000:.2f}%...")
            v3_pool_address = get_v3_pool_address(tokenA['address'], tokenB['address'], fee)
            
            if v3_pool_address:
                pool_info = {
                    "tokenA": tokenA["symbol"],
                    "tokenB": tokenB["symbol"],
                    "tokenA_address": tokenA["address"],
                    "tokenB_address": tokenB["address"],
                    "pool_address": v3_pool_address,
                    "fee": fee
                }
                found_pools_v3.append(pool_info)
                write_json_file('./data/', 'found_pools_v3.json', found_pools_v3)
                print(f"Found Uniswap V3 pool for {tokenA['symbol']} and {tokenB['symbol']} with fee {fee / 10000:.2f}%: {v3_pool_address}")
            else:
                print(f"No Uniswap V3 pool found for {tokenA['symbol']} and {tokenB['symbol']} with fee {fee / 10000:.2f}%.")
