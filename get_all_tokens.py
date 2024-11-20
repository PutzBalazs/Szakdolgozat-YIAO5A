import requests
from utils import write_json_file

def get_uniswap_token_list():
    url = "https://tokens.uniswap.org"
    response = requests.get(url)
    
    if response.status_code == 200:
        token_list = response.json()
        tokens = token_list['tokens']
        formated_tokens = []
        for token in tokens:
            print(f"Token Address: {token['address']}, Symbol: {token['symbol']}")
            t = {
                "symbol": token['symbol'],
                "address": token['address'],
            }
            formated_tokens.append(t)
        return formated_tokens
    else:
        print("Failed to retrieve token list:", response.status_code)
        return []

# Fetch the Uniswap token list
uniswap_tokens = get_uniswap_token_list()
write_json_file("./data/", "ERC20_tokens_v2.json", uniswap_tokens)
