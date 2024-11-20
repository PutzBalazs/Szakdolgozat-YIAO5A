from web3 import Web3
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from utils import eth_node_url, read_json_file

web3 = Web3(Web3.HTTPProvider(eth_node_url))

uniswap_router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D" 
quoter_address = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"  
weth_token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"   
usdt_token_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"   

uniswap_router_abi = read_json_file('./abis/', 'UniswapRouter.json')
router_contract = web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)
quoter_abi = read_json_file('./abis/', 'UniswapV3Quoter.json')
quoter_contract = web3.eth.contract(address=quoter_address, abi=quoter_abi)

fee_tier = 3000
amount_in = web3.to_wei(0.5, 'ether')  
increment_factor = 2  

v2_loss_percentages = []
v3_loss_percentages = []

def calculate_percentage_loss(initial_amount, final_amount):
    return (initial_amount - final_amount) / initial_amount * 100

def price_impact_V2(amount_in):
    # WETH -> USDT swap
    amounts_out_weth_to_usdt = router_contract.functions.getAmountsOut(
        amount_in,
        [weth_token_address, usdt_token_address]
    ).call()
    usdt_received = amounts_out_weth_to_usdt[1]

    # USDT -> WETH swap
    amounts_out_usdt_to_weth = router_contract.functions.getAmountsOut(
        usdt_received,
        [usdt_token_address, weth_token_address]
    ).call()
    final_weth_amount = amounts_out_usdt_to_weth[1]

    # Calculate loss percentage
    loss_percentage = calculate_percentage_loss(amount_in, final_weth_amount)
    print(f"Loss percentage for iteration {i + 1}: {loss_percentage:.2f}%")
    v2_loss_percentages.append(loss_percentage)
    
def price_impact_V3(amount_in):
    # WETH -> USDT swap
    amount_out_usdt = quoter_contract.functions.quoteExactInputSingle(
        weth_token_address,
        usdt_token_address,
        fee_tier,
        amount_in,
        0  
    ).call()

    # USDT -> WETH swap
    amount_out_weth = quoter_contract.functions.quoteExactInputSingle(
        usdt_token_address,
        weth_token_address,
        fee_tier,
        amount_out_usdt,
        0  
    ).call()

    loss_percentage = calculate_percentage_loss(amount_in, amount_out_weth)
    print(f"Loss percentage for iteration {i + 1} (V3): {loss_percentage:.2f}%")
    v3_loss_percentages.append(loss_percentage)

for i in range(10):  
    print(f"Iteration {i + 1}")
    price_impact_V2(amount_in)
    price_impact_V3(amount_in)
    amount_in = int(amount_in * increment_factor)
    
plt.figure(figsize=(10, 6))
iterations = [0.5 * (increment_factor ** i) for i in range(10)]

plt.plot(iterations, v2_loss_percentages, label='Uniswap V2 Loss %', marker='o')
plt.plot(iterations, v3_loss_percentages, label='Uniswap V3 Loss %', marker='o')

plt.xlabel('Input (ETH)')
plt.xscale('log') 
plt.ylabel('Loss Percentage (%)')
plt.title('Comparison of Loss Percentages between Uniswap V2 and V3')

plt.gca().xaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
plt.gca().xaxis.get_major_formatter().set_scientific(False)
plt.gca().yaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
plt.gca().yaxis.get_major_formatter().set_scientific(False)
plt.legend()
plt.grid(True, which="both", linestyle='--', linewidth=0.5)
plt.show()
