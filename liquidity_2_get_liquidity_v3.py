from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from utils import eth_node_url, read_json_file
import json
import matplotlib.pyplot as plt
import numpy as np

web3 = Web3(HTTPProvider(eth_node_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

pools = read_json_file('./', 'data/structured_pools_v3.json')
pool_abi = read_json_file('./', 'abis/UniswapV3Pool.json')

def tick_to_price(tick):
    return 1.0001 ** tick

def get_liquidity_at_ticks(pool):
    try:
        pool_contract = web3.eth.contract(address=Web3.to_checksum_address(pool['pool_address']), abi=pool_abi)
        slot0 = pool_contract.functions.slot0().call()
        tick_spacing = pool_contract.functions.tickSpacing().call()
        current_tick = slot0[1] 
        current_tick = round(current_tick / tick_spacing) * tick_spacing
        tick_liquidity = []
        tick_indexes = []
        
        for i in range(-10, 10):  
            tick_index = current_tick + i * tick_spacing
            tick_info = pool_contract.functions.ticks(tick_index).call()
            liquidity_gross = tick_info[0]  
            tick_liquidity.append(liquidity_gross)
            tick_indexes.append(-1 * tick_index)
            
            print(f"Tick: {tick_index}, Liquidity: {liquidity_gross}")
            
        return tick_indexes, tick_liquidity, current_tick
    except Exception as e:
        print(f"Error fetching liquidity at ticks: {e}")
        return None, None

pool = pools[0]  
token0 = pool['token0']['address']
token1 = pool['token1']['address']
token0_symbol = pool['token0']['symbol']
token1_symbol = pool['token1']['symbol']

tick_indexes, liquidity_levels, current_tick = get_liquidity_at_ticks(pool)

if tick_indexes and liquidity_levels and current_tick:
    plt.figure(figsize=(10, 6))
    bar_width = 0.8 * (tick_indexes[1] - tick_indexes[0]) 
    plt.bar(tick_indexes, liquidity_levels, width=bar_width) 
    plt.axvline(x=-1 * current_tick, color='red', linestyle='--', label="Current Tick")
    plt.yscale('log')
    plt.xlabel(f'Ticks')
    plt.ylabel('Liquidity (Log Scale)')
    plt.title(f'Liquidity Depth for {token0_symbol}/{token1_symbol} Pool Across Ticks')
    plt.grid(True)  
    plt.tight_layout()
    plt.show()

else:
    print("Failed to retrieve tick indexes or liquidity levels.")
