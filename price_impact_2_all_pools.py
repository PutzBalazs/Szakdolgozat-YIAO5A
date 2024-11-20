from web3 import Web3
import time
import matplotlib.pyplot as plt
from utils import eth_node_url, read_json_file, write_json_file

w3 = Web3(Web3.HTTPProvider(eth_node_url))

# Uniswap V2 contract addresses and setup
uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"  # Uniswap V2 Router address
quoter_address = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"  # Uniswap V3 Quoter contract
weth_token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"   # WETH address
usdt_token_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"   # USDT address

uniswap_router_abi = read_json_file('./abis/', 'UniswapRouter.json')
router_contract = w3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)
quoter_abi = read_json_file('./abis/', 'UniswapV3Quoter.json')
quoter_contract = w3.eth.contract(address=quoter_address, abi=quoter_abi)

fee_tier = 3000
amount_in = w3.to_wei(0.5, 'ether')  # Start with 0.5 WETH
increment_factor = 2  # Double each 

def calculate_percentage_loss(initial_amount, final_amount):
    return (initial_amount - final_amount) / initial_amount * 100

def price_impact_V2(amount_in, token0_address, token1_address):
    v2_loss_percentages = []
    for i in range(10):
        # WETH -> USDT swap
        amounts_out_weth_to_usdt = router_contract.functions.getAmountsOut(
            amount_in,
            [token0_address, token1_address]
        ).call()
        usdt_received = amounts_out_weth_to_usdt[1]

        # USDT -> WETH swap
        amounts_out_usdt_to_weth = router_contract.functions.getAmountsOut(
            usdt_received,
            [token1_address, token0_address]
        ).call()
        final_weth_amount = amounts_out_usdt_to_weth[1]

        # Calculate loss %
        loss_percentage = calculate_percentage_loss(amount_in, final_weth_amount)
        print(f"Loss percentage for iteration {i + 1}: {loss_percentage:.2f}%")
        v2_loss_percentages.append(loss_percentage)
        amount_in = int(amount_in * increment_factor)
    return v2_loss_percentages
    
def price_impact_V3(amount_in, token0_address, token1_address):
    v3_loss_percentages = []
    for i in range(10):
        # WETH -> USDT swap
        amount_out_usdt = quoter_contract.functions.quoteExactInputSingle(
            token0_address,
            token1_address,
            fee_tier,
            amount_in,
            0  
        ).call()

        # USDT -> WETH swap
        amount_out_weth = quoter_contract.functions.quoteExactInputSingle(
            token1_address,
            token0_address,
            fee_tier,
            amount_out_usdt,
            0  
        ).call()

        loss_percentage = calculate_percentage_loss(amount_in, amount_out_weth)
        print(f"Loss percentage for iteration {i + 1} (V3): {loss_percentage:.2f}%")
        v3_loss_percentages.append(loss_percentage)
        amount_in = int(amount_in * increment_factor)
    return v3_loss_percentages


v2_struct = []
v3_struct = []
for j in range(2):
    token0_address = read_json_file('./data/', 'ERC20_tokens.json')[0]['address']
    token1_address = read_json_file('./data/', 'ERC20_tokens.json')[j+1]['address']
    token0_address = w3.to_checksum_address(token0_address)
    token1_address = w3.to_checksum_address(token1_address)
    print(token0_address)
    print(token1_address)
    v2_struct_j =  price_impact_V2(amount_in, token0_address, token1_address)
    v3_struct_j = price_impact_V3(amount_in, token0_address, token1_address)
    v2_struct.append({
        'token0': token0_address,
        'token1': token1_address,
        'data': v2_struct_j
    })
    v3_struct.append({
        'token0': token0_address,
        'token1': token1_address,
        'data': v3_struct_j
    })
    

write_json_file('./compiled_data/', 'v2_loss_percentages.json', v2_struct)
write_json_file('./compiled_data/', 'v3_loss_percentages.json', v3_struct)
    

