import json

run_on_eth_node=False

def read_json_file(directory:str, file_name: str):
    try:
        file_path = directory + file_name
        with open(file_path, 'r') as f_:
            json_data = json.load(f_)
    except Exception as e:
        print(f"Unable to open the {file_path} file")
        raise e
    return json_data

def write_json_file(directory: str, file_name: str, data: dict):
    try:
        file_path = directory + file_name
        with open(file_path, 'w') as f_:
            json.dump(data, f_, indent=4)
    except Exception as e:
        print(f"Unable to write to the {file_path} file")
        raise e

if run_on_eth_node:
    eth_node_url = "http://localhost:8545"
else:
    eth_node_url = 'https://eth-mainnet.g.alchemy.com/v2/hu30AzU_3kcnOWkM146g5lHXtPSZDevA'
