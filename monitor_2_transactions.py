from web3 import Web3, HTTPProvider
from utils import eth_node_url
import json, time
import matplotlib.pyplot as plt
import pandas as pd

transactions = []
web3 = Web3(HTTPProvider(eth_node_url))

def handle_new_block(block_number):
    block = web3.eth.get_block(block_number, full_transactions=True)
    for tx in block.transactions:
        tx_dict = dict(tx)
        tx_dict['value_ether'] = web3.from_wei(tx_dict['value'], 'ether')
        transactions.append(tx_dict)

latest_block = web3.eth.block_number
for i in range(5): 
    handle_new_block(latest_block - i)

df = pd.DataFrame(transactions)
df['value_ether'] = pd.to_numeric(df['value_ether'], errors='coerce') 
df = df.dropna(subset=['value_ether']) 

# Transaction values
plt.figure(figsize=(10, 6))
plt.hist(df['value_ether'], bins=30, color='blue', edgecolor='black')
plt.yscale('log')
plt.title("Distribution of Transaction Values (Ether)")
plt.xlabel("Transaction Value (Ether)")
plt.ylabel("Frequency (Log Scale)")
plt.tight_layout()
plt.show()

# Gas price distribution
plt.figure(figsize=(10,6))
plt.bar(df.index, df['gasPrice'].astype(float) / 10**9)
plt.yscale('log')
plt.title("Gas Prices in Gwei")
plt.xlabel("Transaction Index")
plt.ylabel("Gas Price (Gwei)")
plt.show()
