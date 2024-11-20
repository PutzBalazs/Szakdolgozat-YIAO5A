from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from utils import eth_node_url, read_json_file
import json, time
import matplotlib.pyplot as plt
import pandas as pd

web3 = Web3(HTTPProvider(eth_node_url))

block_data = []
latest_block = web3.eth.block_number
previous_block_timestamp = None 

for i in range(50):
    block = web3.eth.get_block(latest_block - i, full_transactions=True)
    
    block_creation_time = None
    if previous_block_timestamp:
        block_creation_time = (block['timestamp'] - previous_block_timestamp)
    previous_block_timestamp = block['timestamp']
    
    block_info = {
        "Block": block['number'],
        "Creation Time": block_creation_time,
        "Txn": len(block['transactions']),
        "Fee Recipient": block['miner'],
        "Gas Used": web3.from_wei(block['gasUsed'], 'wei'),
        "Gas Limit": web3.from_wei(block['gasLimit'], 'wei'),
        "Base Fee (Gwei)": web3.from_wei(block['baseFeePerGas'], 'gwei') if 'baseFeePerGas' in block else None,
    }
    block_data.append(block_info)

df_blocks = pd.DataFrame(block_data)

# Gas Used vs Gas Limit
plt.figure(figsize=(10,6))
plt.bar(df_blocks['Block'], df_blocks['Gas Used'], color='blue', label='Gas Used (wei)')
plt.bar(df_blocks['Block'], df_blocks['Gas Limit'], alpha=0.5, color='orange', label='Gas Limit')
plt.title("Gas Used vs Gas Limit for Blocks")
plt.xlabel("Block Number")
plt.ylabel("Gas (wei)")
plt.legend()
plt.show()

# Number of Transactions per Block
plt.figure(figsize=(10,6))
plt.bar(df_blocks['Block'], df_blocks['Txn'], color='purple')
plt.title("Number of Transactions per Block")
plt.xlabel("Block Number")
plt.ylabel("Number of Transactions")
plt.show()

# Block Creation Delay in milliseconds
plt.figure(figsize=(10,6))
plt.plot(df_blocks['Block'], -1 * df_blocks['Creation Time'], marker='o', color='blue', label='Block Creation Time (s)')
plt.title("Block Creation Times")
plt.xlabel("Block Number")
plt.ylabel("Creation Time (s)")
plt.legend()
plt.show()
