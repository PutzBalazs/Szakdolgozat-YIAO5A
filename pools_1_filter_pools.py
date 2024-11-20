import requests
import json
from datetime import datetime, timedelta
from utils import read_json_file, write_json_file

api_key = "HMXH8I1DV8E8KV1IZGY8UFNQGQUUAP3BHW"

def get_recent_transfers(pool_address, api_key):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={pool_address}&startblock=latest&endblock=latest&sort=desc&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == '1':
            return data.get('result', [])
    except requests.RequestException as e:
        print(f"Request error for pool {pool_address}: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error for pool {pool_address}: {e}")
    except Exception as e:
        print(f"Unexpected error for pool {pool_address}: {e}")
    return []

def filter_active_pools(pool_data, api_key, path):
    active_pools = []
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=10)
    thirty_days_ago_timestamp = int(thirty_days_ago.timestamp())
    
    for pool in pool_data:
        try:
            print(f"Processing pool {pool}...")
            last_transfer = get_recent_transfers(pool, api_key)
            if not last_transfer:
                print(f"Pool {pool} has no recent transfers, skipping")
                continue
            else:
                last_transfer_timestamp = int(last_transfer[0].get('timeStamp', 0))
                if last_transfer_timestamp < thirty_days_ago_timestamp:
                    print(f"Pool {pool} has no recent transfers, skipping")
                    continue
                else:
                    active_pools.append(pool)
                    print(f"Pool {pool} is active")
                    write_json_file('./data/', path, active_pools)
                              
        except Exception as e:
            print(f"Error processing pool {pool}: {e}")
    write_json_file('./data/', path, active_pools)
    return active_pools

def main():
    try:    
        #filter v2 pools
        save_path = 'active_uniswap_v2_pools.json'
        pools = []
        file = read_json_file('./data/', 'found_pools_v2.json')
        for f in file:
            pools.append(f['pool_address'])
        print("Loaded pool addresses:", len(pools))
        
        active_pools = filter_active_pools(pools, api_key, save_path)
        print("Active Uniswap pools data saved to {save_path}")
        
        #filter v3 pools
        save_path = 'active_uniswap_v3_pools.json'
        pools = []
        file = read_json_file('./data/', 'found_pools_v3.json')
        for f in file:
            pools.append(f['pool_address'])
        print("Loaded pool addresses:", len(pools))
        active_pools = filter_active_pools(pools, api_key, save_path)
        print("Active Uniswap pools data saved to {save_path}")
            
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
