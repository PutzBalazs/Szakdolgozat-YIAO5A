from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from utils import eth_node_url, read_json_file
import json
import numpy as np
import matplotlib.pyplot as plt

web3 = Web3(HTTPProvider(eth_node_url))
pool_abi = read_json_file('./', 'abis/UniswapV2Pair.json')
token_abi = read_json_file('./', 'abis/ERC20.json')

def calculate_edges(pool):
    try:
        token0 = pool['token0']['address']
        token1 = pool['token1']['address']
        token0_symbol = pool['token0']['symbol']
        token1_symbol = pool['token1']['symbol']
        token0_decimals = pool['token0']['decimals']
        token1_decimals = pool['token1']['decimals']

        checksum_address = Web3.to_checksum_address(pool['pool_address'])
        pool_contract = web3.eth.contract(address=checksum_address, abi=pool_abi)
        reserves = pool_contract.functions.getReserves().call()
        reserve0 = reserves[0] / (10 ** token0_decimals)  
        reserve1 = reserves[1] / (10 ** token1_decimals)  
        print(f'{token0_symbol} reserve: {reserve0}, {token1_symbol} reserve: {reserve1}')
        plot_amm_curve(reserve0, reserve1, token0_symbol, token1_symbol)

    except Exception as e:
        print(f"Failed to calculate edges: {e}")

def plot_amm_curve(reserve0, reserve1, token0_symbol, token1_symbol):
    print("Plotting AMM curve...")
    """Plot the AMM curve for a given pair of reserves"""
    k = reserve0 * reserve1  # Constant product k
    x_values = np.linspace(0.01 * reserve0, 2 * reserve0, 500)  

    # Calculate constant product formula: y = k / x
    y_values = k / x_values

    # Plot the AMM curve
    plt.figure(figsize=(8,6))
    plt.plot(x_values, y_values, label=f'AMM Curve (k={k})')
    plt.axvline(x=reserve0, color='r', linestyle='--', label=f'Reserve {token0_symbol}={reserve0}')
    plt.axhline(y=reserve1, color='g', linestyle='--', label=f'Reserve {token1_symbol}={reserve1}')
    plt.title(f'AMM Curve for {token0_symbol}/{token1_symbol}')
    plt.xlabel(f'{token0_symbol} Reserves (x)')
    plt.ylabel(f'{token1_symbol} Reserves (y)')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    pool = read_json_file('./data/', 'structured_pools_v2.json')[0]
    try:  
        calculate_edges(pool)
    except Exception as e:
        print(f"Query to pool failed: {e} {pool}")

if __name__ == "__main__":
    main()
