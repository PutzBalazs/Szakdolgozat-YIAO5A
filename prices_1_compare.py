import requests
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from web3 import Web3, HTTPProvider
from utils import eth_node_url, read_json_file, write_json_file

web3 = Web3(HTTPProvider(eth_node_url))

pool_abi_v2 = read_json_file('./abis/', 'UniswapV2Pair.json')  
token_abi_v2 = read_json_file('./abis/', 'ERC20.json')

pool_abi_v3 = read_json_file('./abis/', 'UniswapV3Pool.json')
token_abi_v3 = read_json_file('./abis/', 'ERC20.json')

def get_historical_data_v2(pool, from_block, to_block, interval=1000):
    pool_address = pool['pool_address']
    token0 = pool['token0']
    token1 = pool['token1']
    token0_decimals = token0['decimals']
    token1_decimals = token1['decimals']
    prices = []
    for block in range(from_block, to_block, interval):
        pool_contract = web3.eth.contract(address=pool_address, abi=pool_abi_v2)
        reserves = pool_contract.functions.getReserves().call(block_identifier=block)
        price = reserves[1] / reserves[0]  
        price = price * 10 ** (token0_decimals - token1_decimals)
        timestamp = web3.eth.get_block(block)['timestamp']
        prices.append((timestamp, price))
    return prices

# One block approximately 12 seconds -> 1200 blocks in 4 hours
def get_historical_data_v3(pool, from_block, to_block, interval=1200):
    pool_address = pool['pool_address']
    token0 = pool['token0']
    token1 = pool['token1']
    token0_decimals = token0['decimals']
    token1_decimals = token1['decimals']
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

def get_binance_historical_prices(symbol, start_time, end_time, interval='4h'):
    url = f'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time * 1000,  
        'endTime': end_time * 1000 
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    binance_prices = []
    for candle in data:
        timestamp = candle[0] / 1000  
        close_price = float(candle[4])  
        binance_prices.append((timestamp, close_price))
    
    return binance_prices

def plot_price_comparison(v2_prices, v3_prices, binance_prices):
    v2_timestamps, v2_prices = zip(*v2_prices)
    v3_timestamps, v3_prices = zip(*v3_prices)
    binance_timestamps, binance_prices = zip(*binance_prices)

    v2_dates = [datetime.fromtimestamp(ts) for ts in v2_timestamps]
    v3_dates = [datetime.fromtimestamp(ts) for ts in v3_timestamps]
    binance_dates = [datetime.fromtimestamp(ts) for ts in binance_timestamps]

    plt.figure(figsize=(12, 6))
    
    plt.plot(v2_dates, v2_prices, label='Uniswap V2 (ETH/USDT)', color='blue', marker='o', linestyle='-', linewidth=2)
    plt.plot(v3_dates, v3_prices, label='Uniswap V3 (ETH/USDT)', color='green', marker='s', linestyle='--', linewidth=2)
    plt.plot(binance_dates, binance_prices, label='Binance (ETH/USDT)', color='red', marker='^', linestyle='-.', linewidth=2)

    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Price (USDT)', fontsize=14)
    plt.title('ETH/USDT Price Comparison: Uniswap V2, V3 vs Binance', fontsize=16)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gcf().autofmt_xdate()

    plt.grid(True)
    plt.legend(loc='best', fontsize=12)
    plt.tight_layout()
    plt.show()

# Load pool data
v2_pool = read_json_file('./data/', 'structured_pools_v2.json')[0]  # ETH/USDC V2 pool
v3_pool = read_json_file('./data/', 'structured_pools_v3.json')[0]  # ETH/USDC V3 pool

latest_block = web3.eth.get_block('latest')['number']
from_block = latest_block - 30000
to_block = latest_block

v2_prices = get_historical_data_v2(v2_pool, from_block, to_block)
v3_prices = get_historical_data_v3(v3_pool, from_block, to_block)

# Get Binance prices
start_time = web3.eth.get_block(from_block)['timestamp']
end_time = web3.eth.get_block(to_block)['timestamp']
binance_prices = get_binance_historical_prices('ETHUSDT', start_time, end_time)

print("Uniswap V2 Prices:", v2_prices)
print("Uniswap V3 Prices:", v3_prices)
print("Binance Prices:", binance_prices)

# Plot price comparison 
plot_price_comparison(v2_prices, v3_prices, binance_prices)
