from web3 import Web3, HTTPProvider
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import eth_node_url, read_json_file, run_on_eth_node

web3 = Web3(HTTPProvider(eth_node_url))
pool_abi = read_json_file('./', 'abis/UniswapV3Pool.json')
pools = read_json_file('./', 'data/active_uniswap_v3_pools.json')
latest_block = web3.eth.block_number
lookback_blocks = 2
start_block = latest_block - lookback_blocks + 1

transaction_stats = defaultdict(lambda: {"swaps": 0, "mints": 0, "burns": 0, "collects": 0, "transfers": 0, "total_txn": 0})

# Event signatures
swap_event_signature = web3.keccak(text="Swap(address,address,int256,int256,uint160,uint128,int24)").hex()
mint_event_signature = web3.keccak(text="Mint(address,address,int24,int24,uint128,uint256,uint256)").hex()
burn_event_signature = web3.keccak(text="Burn(address,int24,int24,uint128)").hex()
collect_event_signature = web3.keccak(text="Collect(address,address,int24,int24,uint128,uint128)").hex()
transfer_event_signature = web3.keccak(text="Transfer(address,address,uint256)").hex()

def fetch_events_for_block_range(pool_address, start_block, end_block):
    checksum_address = Web3.to_checksum_address(pool_address)
    pool_contract = web3.eth.contract(address=checksum_address, abi=pool_abi)

    # Swap, Mint, Burn, Collect 
    swap_events = pool_contract.events.Swap.create_filter(fromBlock=start_block, toBlock=end_block).get_all_entries()
    mint_events = pool_contract.events.Mint.create_filter(fromBlock=start_block, toBlock=end_block).get_all_entries()
    burn_events = pool_contract.events.Burn.create_filter(fromBlock=start_block, toBlock=end_block).get_all_entries()
    collect_events = pool_contract.events.Collect.create_filter(fromBlock=start_block, toBlock=end_block).get_all_entries()

    return swap_events, mint_events, burn_events, collect_events

def fetch_unique_events_for_block(block_number):
    block = web3.eth.get_block(block_number, full_transactions=False)
    unique_event_txns = {
        "swaps": set(),
        "mints": set(),
        "burns": set(),
        "collects": set(),
        "transfers": set()
    }

    # Check each transaction log in the block
    for tx_hash in block['transactions']:
        receipt = web3.eth.get_transaction_receipt(tx_hash)
        for log in receipt['logs']:
            # Check that the log has topics before trying to access them
            if log['topics']:
                # Check for each event type and add to respective set (ensuring no double counting)
                if log['topics'][0].hex() == swap_event_signature:
                    unique_event_txns["swaps"].add(tx_hash)
                elif log['topics'][0].hex() == mint_event_signature:
                    unique_event_txns["mints"].add(tx_hash)
                elif log['topics'][0].hex() == burn_event_signature:
                    unique_event_txns["burns"].add(tx_hash)
                elif log['topics'][0].hex() == collect_event_signature:
                    unique_event_txns["collects"].add(tx_hash)
                elif log['topics'][0].hex() == transfer_event_signature:
                    unique_event_txns["transfers"].add(tx_hash)

    return unique_event_txns


# Fetch total transaction count for each block
def fetch_total_transactions_for_block(block_number):
    block = web3.eth.get_block(block_number, full_transactions=False)
    return len(block['transactions'])

# Fetch Transfer and other unique events per block, ensuring no double counting
for block_number in range(start_block, latest_block + 1):
    unique_events = fetch_unique_events_for_block(block_number)
    print(f"Block {block_number}: {len(unique_events['swaps'])} swaps, {len(unique_events['mints'])} mints, {len(unique_events['burns'])} burns, {len(unique_events['collects'])} collects, {len(unique_events['transfers'])} transfers")
    transaction_stats[block_number]["transfers"] = len(unique_events["transfers"])
    transaction_stats[block_number]["swaps"] += len(unique_events["swaps"])
    transaction_stats[block_number]["mints"] += len(unique_events["mints"])
    transaction_stats[block_number]["burns"] += len(unique_events["burns"])
    transaction_stats[block_number]["collects"] += len(unique_events["collects"])
    transaction_stats[block_number]["total"] = fetch_total_transactions_for_block(block_number)

df_stats = pd.DataFrame.from_dict(transaction_stats, orient='index').sort_index()
print(df_stats)
df_stats.to_csv('compiled_data/transaction_stats.csv', index=True)