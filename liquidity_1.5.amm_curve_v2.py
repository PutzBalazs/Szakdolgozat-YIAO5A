from web3 import Web3, HTTPProvider
import json
from utils import read_json_file, eth_node_url
import matplotlib.pyplot as plt

web3 = Web3(HTTPProvider(eth_node_url))

quoter_abi = read_json_file('./abis/', 'UniswapV3Quoter.json')
quoter_address_v3 = '0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6'  
quoter_contract = web3.eth.contract(address=quoter_address_v3, abi=quoter_abi)

def get_quotes_for_usd_range(usd_amounts, pool):
    token0 = pool['token0']['address']
    token1 = pool['token1']['address']
    token0_decimals = pool['token0']['decimals']
    token1_decimals = pool['token1']['decimals']

    quotes = []
    for usd_amount in usd_amounts:
        amount_in = int(usd_amount * (10 ** token0_decimals)) 
        try:
            quote = quoter_contract.functions.quoteExactInputSingle(
                token0,            
                token1,            
                3000,              
                amount_in,         
                0                  
            ).call()
            
            amount_out = quote / (10 ** token1_decimals)
            quotes.append(amount_out)
            print(f"USD {usd_amount} -> {amount_out:.6f} WETH")
        
        except Exception as e:
            print(f"Error getting quote for {usd_amount} USD: {e}")
            quotes.append(0)  
    
    return quotes

def plot_quotes(usd_amounts, quotes):
    """Plot the quotes as a line chart."""
    plt.figure(figsize=(8,6))
    plt.plot(usd_amounts, quotes, marker='o', label='WETH to USD')
    plt.title('WETH to USD Quote Curve')
    plt.xlabel('WETH Amount')
    plt.ylabel('USD Received')
    plt.grid(True)
    plt.legend()
    plt.show()

usd_amounts = range(15000,21000,500)  
pool = read_json_file('./data/', 'structured_pools_v2.json')[0]
quotes = get_quotes_for_usd_range(usd_amounts, pool)
plot_quotes(usd_amounts, quotes)
