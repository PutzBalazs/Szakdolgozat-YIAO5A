import numpy as np
import matplotlib.pyplot as plt
from utils import read_json_file

directory = './compiled_data/'
v2_file = 'v2_loss_percentages.json'
v3_file = 'v3_loss_percentages.json'

def calculate_average_slippage(slippage_data):
    all_slippages = [pool['data'] for pool in slippage_data]
    avg_slippages = np.mean(all_slippages, axis=0)
    return avg_slippages

def plot_loss_percentages(iterations, v2_loss_percentages, v3_loss_percentages):
    plt.figure(figsize=(10, 6))

    plt.plot(iterations, v2_loss_percentages, label='Uniswap V2 Loss %', marker='o')
    plt.plot(iterations, v3_loss_percentages, label='Uniswap V3 Loss %', marker='o')

    plt.xlabel('Input (ETH)')
    plt.ylabel('Loss Percentage (%)')
    plt.title('Comparison of Loss Percentages between Uniswap V2 and V3')
    plt.xscale('log')  
    plt.legend()
    plt.grid(True, which="both", linestyle='--', linewidth=0.5)

    plt.show()

def main():
    v2_data = read_json_file(directory, v2_file)
    v3_data = read_json_file(directory, v3_file)
    
    v2_avg_slippage = calculate_average_slippage(v2_data)
    v3_avg_slippage = calculate_average_slippage(v3_data)
    
    iterations = range(1, 11) 
    values = [0.5 * (2 ** i) for i in range(10)]
    iterations = values
    plot_loss_percentages(iterations, v2_avg_slippage, v3_avg_slippage) 

if __name__ == "__main__":
    main()
