import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from utils import read_json_file

V2_SUBGRAPH_URL = "https://gateway.thegraph.com/api/5de7b2eb43f03f86b0ee04c4f53c1955/subgraphs/id/EYCKATKGBKLWvSfwvBjzfCBmGwYNdVkduYXVivCsLRFu"
V3_SUBGRAPH_URL = "https://gateway.thegraph.com/api/5de7b2eb43f03f86b0ee04c4f53c1955/subgraphs/id/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"

def run_query(url, query):
    response = requests.post(url, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")

def fetch_trading_volume(pool_address, start_timestamp, end_timestamp, url, is_v2=True):
    all_swaps = []
    skip = 0
    while True:
        if is_v2:
            query = f"""
            {{
              swaps(first: 1000, skip: {skip}, where: {{pair: "{pool_address.lower()}", timestamp_gte: {start_timestamp}, timestamp_lte: {end_timestamp}}}, orderBy: timestamp, orderDirection: asc) {{
                amount0In
                amount0Out
                timestamp
              }}
            }}
            """
        else:
            query = f"""
            {{
              swaps(first: 1000, skip: {skip}, where: {{pool: "{pool_address.lower()}", timestamp_gte: {start_timestamp}, timestamp_lte: {end_timestamp}}}, orderBy: timestamp, orderDirection: asc) {{
                amount0
                timestamp
              }}
            }}
            """
        data = run_query(url, query)
        swaps = data['data']['swaps']
        all_swaps.extend(swaps)
        if len(swaps) < 1000:
            break
        skip += 1000
    return all_swaps

def process_daily_trading_data(trades, start_date, end_date, token0_price):
    daily_volume = {start_date.date() + timedelta(days=i): 0 for i in range((end_date.date() - start_date.date()).days + 1)}
    for trade in trades:
        trade_time = datetime.fromtimestamp(int(trade['timestamp']), tz=timezone.utc)
        trade_date = trade_time.date()
        if 'amount0' in trade:
            volume0 = abs(float(trade['amount0'])) * token0_price
        else:
            volume0 = abs(float(trade['amount0In']) + float(trade['amount0Out'])) * token0_price
        daily_volume[trade_date] += volume0
    return daily_volume

def plot_combined_trading_volume(v2_volume, v3_volume, token0_symbol):
    dates = sorted(set(v2_volume.keys()).union(set(v3_volume.keys())))
    v2_volumes = [v2_volume.get(date, 0) for date in dates]
    v3_volumes = [v3_volume.get(date, 0) for date in dates]

    bar_width = 0.35
    x_indexes = list(range(len(dates)))

    plt.figure(figsize=(14, 7))
    plt.bar([x - bar_width/2 for x in x_indexes], v2_volumes, width=bar_width, label=f'{token0_symbol} Volume (Uniswap V2)', color='blue')
    plt.bar([x + bar_width/2 for x in x_indexes], v3_volumes, width=bar_width, label=f'{token0_symbol} Volume (Uniswap V3)', color='green')

    plt.xlabel("Day")
    plt.ylabel("Trading Volume (USD)")
    plt.title(f"Daily Trading Volume for {token0_symbol} on Uniswap V2 and V3")
    plt.xticks(ticks=x_indexes, labels=[date.strftime('%Y-%m-%d') for date in dates], rotation=45)
    plt.legend()
    plt.grid(True)
    
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    plt.tight_layout()
    plt.show()

def main():
    pool_v2 = read_json_file('./data/', 'structured_pools_v2.json')[0]
    pool_v3 = read_json_file('./data/', 'structured_pools_v3.json')[0]
    pool_address_v2 = pool_v2['pool_address']
    pool_address_v3 = pool_v3['pool_address']

    token0_price = 1  
    end_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=10)

    trades_v2 = fetch_trading_volume(pool_address_v2, int(start_date.timestamp()), int(end_date.timestamp()), V2_SUBGRAPH_URL, is_v2=True)
    trades_v3 = fetch_trading_volume(pool_address_v3, int(start_date.timestamp()), int(end_date.timestamp()), V3_SUBGRAPH_URL, is_v2=False)
    daily_volume_v2 = process_daily_trading_data(trades_v2, start_date, end_date, token0_price)
    daily_volume_v3 = process_daily_trading_data(trades_v3, start_date, end_date, token0_price)

    token0_symbol = pool_v2['token0']['symbol']
    plot_combined_trading_volume(daily_volume_v2, daily_volume_v3, token0_symbol)

if __name__ == "__main__":
    main()
