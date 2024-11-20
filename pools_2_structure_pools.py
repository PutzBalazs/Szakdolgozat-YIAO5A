from web3 import Web3, HTTPProvider
from utils import eth_node_url, read_json_file, write_json_file

web3 = Web3(HTTPProvider(eth_node_url))
pool_abi_v2 = read_json_file('./abis/', 'UniswapV2Pair.json') 
token_abi_v2 = read_json_file('./abis/', 'ERC20.json')
pool_abi_v3 = read_json_file('./abis/', 'UniswapV3Pool.json')
token_abi_v3 = read_json_file('./abis/', 'ERC20.json')
structured_pools_v2 = []
structured_pools_v3 = []

def calculate_edges_v2(pool):
    token0_decimals = 0
    token1_decimals = 0
    token0 = pool.functions.token0().call()
    token1 = pool.functions.token1().call()
    print(f'token0: {token0}, token1: {token1}')
    
    try:
        token0_info = web3.eth.contract(web3.to_checksum_address(token0), abi=token_abi_v2)
        token0_symbol = token0_info.functions.symbol().call()
        token0_decimals = token0_info.functions.decimals().call()

        token1_info = web3.eth.contract(web3.to_checksum_address(token1), abi=token_abi_v2)
        token1_symbol = token1_info.functions.symbol().call()
        token1_decimals = token1_info.functions.decimals().call()
    except Exception as e:
        print(f"Error fetching token info: {e}")
        return

    try:
        # Get the reserves
        reserves = pool.functions.getReserves().call()
        reserve0 = reserves[0]
        reserve1 = reserves[1]

        # Calculate token prices using reserves
        token0_price = (reserve0 / reserve1) * 10 ** (token1_decimals - token0_decimals)
        token1_price = (reserve1 / reserve0) * 10 ** (token0_decimals - token1_decimals)
        
        data = {
            'pool_address': pool.address,
            'token0_price': token0_price,
            'token1_price': token1_price,
            'token0': {
                'address': token0,
                'symbol': token0_symbol,
                'decimals': token0_decimals
            },
            'token1': {
                'address': token1,
                'symbol': token1_symbol,
                'decimals': token1_decimals
            }
        }
        structured_pools_v2.append(data)
        write_json_file('data/', 'structured_pools_v2.json', structured_pools_v2)
        
    except Exception as e:
        print(f"Error calculating pool edges: {e}")
        return

def calculate_edges_v3(pool):
    token0_decimals = 0
    token1_decimals = 0
    token0 = pool.functions.token0().call()
    token1 = pool.functions.token1().call()
    print(f'token0: {token0}, token1: {token1}')
    
    try:
        token0_info = web3.eth.contract(web3.to_checksum_address(token0), abi=token_abi_v3)
        token0_symbol = token0_info.functions.symbol().call()
        token0_decimals = token0_info.functions.decimals().call()
        token1_info = web3.eth.contract(web3.to_checksum_address(token1), abi=token_abi_v3)
        token1_symbol = token1_info.functions.symbol().call()
        token1_decimals = token1_info.functions.decimals().call()
        fee = pool.functions.fee().call()
       
    except Exception as e:
        print(f"Error fetching token info: {e}")
        return
    
    try:
        slot0 = pool.functions.slot0().call()
        sqrtPriceX96 = slot0[0]
        sqrtPriceX192 = sqrtPriceX96 ** 2
        token1Price = sqrtPriceX192 / 2 ** 192
        token0Price = 1 / token1Price
        
        token0_price = token0Price * 10 ** (token1_decimals - token0_decimals)
        token1_price = token1Price * 10 ** (token0_decimals - token1_decimals)
        
        data = {
            'pool_address': pool.address,
            'token0_price': token0_price,
            'token1_price': token1_price,
            'token0': {
                'address': token0,
                'symbol': token0_symbol,
                'decimals': token0_decimals
            },
            'token1': {
                'address': token1,
                'symbol': token1_symbol,
                'decimals': token1_decimals
            },
            'fee': fee
        }
        structured_pools_v3.append(data)
        write_json_file('data/', 'structured_pools_v3.json', structured_pools_v3)
        
    except Exception as e:
        print(f"Error calculating pool edges: {e}")
        return


def main():
    # structure v2 pools
    pool_addresses = read_json_file("data/", "active_uniswap_v2_pools.json")
    print("Loaded pool addresses:", len(pool_addresses))
    
    for pool_address in pool_addresses:
        try:
            checksum_address = Web3.to_checksum_address(pool_address)
            pool_contract = web3.eth.contract(address=checksum_address, abi=pool_abi_v2)
            print(f"Processing pool {pool_address}, contract: {pool_contract}")
            calculate_edges_v2(pool_contract)
            print(".")
        except Exception as e:
            print(f"Query to pool failed: {e} {pool_address}")
        
    print(f'Found {len(structured_pools_v2)} pools')

    # structure v3 pools
    pool_addresses = read_json_file("data/", "active_uniswap_v3_pools.json")
    print("Loaded pool addresses:", len(pool_addresses))
    
    for pool_address in pool_addresses:
        try:
            checksum_address = Web3.to_checksum_address(pool_address)
            pool_contract = web3.eth.contract(address=checksum_address, abi=pool_abi_v3)
            print(f"Processing pool {pool_address}, contract: {pool_contract}")
            calculate_edges_v3(pool_contract)
            print(".")
        except Exception as e:
            print(f"Query to pool failed: {e} {pool_address}")
        
    print(f'Found {len(structured_pools_v3)} pools')
    
if __name__ == "__main__":
    main()
