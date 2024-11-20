import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from utils import eth_node_url, read_json_file

ETHERSCAN_API_KEY = "HMXH8I1DV8E8KV1IZGY8UFNQGQUUAP3BHW"
WALLET_ADDRESS = '0x8315177ab297ba92a06054ce80a67ed4dbd7ed3a'

web3 = Web3(HTTPProvider(eth_node_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)
pool_abi_v3 = read_json_file('./abis/', 'UniswapV3Pool.json')

def get_historical_data_v3(pool, from_block, to_block, interval):
    pool_address = pool['pool_address']
    token0_decimals = pool['token0']['decimals']
    token1_decimals = pool['token1']['decimals']
    prices = []
    for block in range(from_block, to_block, interval):
        pool_contract = web3.eth.contract(address=pool_address, abi=pool_abi_v3)
        slot0 = pool_contract.functions.slot0().call(block_identifier=block)
        sqrtPriceX96 = slot0[0]
        price = (sqrtPriceX96 ** 2) / (2 ** 192)
        price = price * 10 ** (token0_decimals - token1_decimals)
        timestamp = web3.eth.get_block(block)['timestamp']
        prices.append((timestamp, price))
    return prices
    
def normalize_data(data):
    first_value = data[0]
    if first_value == 0:
        return 0
    return [(value / first_value - 1) * 100 for value in data]

# Normalize and plot the data
def plot_normalized_data(timestamps, v3_prices, whale_balances):
    dates = [datetime.fromtimestamp(ts) for ts in timestamps]
    normalized_prices = normalize_data(v3_prices)
    normalized_balances = normalize_data(whale_balances)
    
    plt.figure(figsize=(12, 6))
    plt.plot(dates, normalized_prices, label='Normalized Uniswap V3 Prices', color='blue', marker='o', linestyle='-', linewidth=2)
    plt.plot(dates, normalized_balances, label='Normalized Whale Wallet Balances', color='red', marker='o', linestyle='--', linewidth=2)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Normalized % Change', fontsize=14)
    plt.title('Comparison of Uniswap V3 Prices and Whale Wallet Balances', fontsize=16)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()
    plt.grid(True)
    plt.legend(loc='best', fontsize=12)
    plt.tight_layout()
    plt.show()

def get_wallet_balance_at_block(wallet_address, block_number):
    try:
        wallet_address = Web3.to_checksum_address(wallet_address)
        balance_wei = web3.eth.get_balance(wallet_address, block_identifier=block_number)
        balance_eth = balance_wei / 10**18
        return balance_eth
    except Exception as e:
        print(f"Error fetching balance for block {block_number}: {e}")
        return None  
    
def main():
    v3_pool = read_json_file('./data/', 'structured_pools_v3.json')[0]
    latest_block = web3.eth.get_block('latest')['number']
    days_to_fetch = 365 
    blocks_per_day = 7200  # number of blocks per day on Ethereum
    interval = blocks_per_day * 7

    from_block = latest_block - (days_to_fetch * blocks_per_day)
    to_block = latest_block

    v3_prices_data = get_historical_data_v3(v3_pool, from_block, to_block, interval=interval)
    timestamps, v3_prices = zip(*v3_prices_data)

    whale_balances = []
    valid_timestamps = []  
    
    for i, block in enumerate(range(from_block, to_block, interval)):
        balance = get_wallet_balance_at_block(WALLET_ADDRESS, block)
        if balance is not None:  
            whale_balances.append(balance)
            valid_timestamps.append(timestamps[i])  


    if len(valid_timestamps) != len(whale_balances):
        print("Warning: Mismatch in the number of timestamps and balances retrieved.")
        print(f"Timestamps retrieved: {len(valid_timestamps)}, Balances retrieved: {len(whale_balances)}")
        return
    
    plot_normalized_data(valid_timestamps, v3_prices, whale_balances)

if __name__ == "__main__":
    main()
