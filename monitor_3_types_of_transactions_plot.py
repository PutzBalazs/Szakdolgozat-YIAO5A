import pandas as pd
import matplotlib.pyplot as plt

df_stats = pd.read_csv('compiled_data/transaction_stats.csv', index_col=0)
df_stats['others'] = df_stats['total'] - df_stats[['swaps', 'mints', 'burns', 'collects', 'transfers']].sum(axis=1)
df_stats = df_stats[['swaps', 'mints', 'burns', 'collects', 'transfers', 'others', 'total']]
df_avg_stats = df_stats[['swaps', 'mints', 'burns', 'collects', 'others', 'total']].mean().to_frame().T

# Plot the average transaction types
df_avg_stats.plot(kind='bar', stacked=False, figsize=(10, 6))
plt.xticks(rotation=0)
plt.yscale('log')
plt.title('Average Transaction Type Counts')
plt.xlabel('Transaction Type')
plt.ylabel('Average Count')
plt.legend(loc='upper right')
plt.show()
