import json
import networkx as nx
import matplotlib.pyplot as plt
from utils import read_json_file


def create_graph_from_pools(pool_data):
    G = nx.DiGraph()

    for pool in pool_data:
        token0 = pool['token0']
        token1 = pool['token1']
        token0_symbol = token0['symbol']
        token1_symbol = token1['symbol']

        # Add nodes for each token
        if not G.has_node(token0_symbol):
            G.add_node(token0_symbol, **token0)
        if not G.has_node(token1_symbol):
            G.add_node(token1_symbol, **token1)
            
        # Add edges
        G.add_edge(token0_symbol, token1_symbol, direction="fw", pool=pool['pool_address'])
        G.add_edge(token1_symbol, token0_symbol, direction="bw", pool=pool['pool_address'])
    return G

def visualize_graph(G, title='Graph'):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='skyblue', edge_color='gray', font_size=10, font_weight='bold')
    labels = nx.get_edge_attributes(G, 'price')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title(title, fontsize=15)
    plt.show()

def remove_single_edge_nodes(G):
    nodes_to_remove = [node for node, degree in G.degree() if degree == 2]
    G.remove_nodes_from(nodes_to_remove)
    return G

pool_data_v2 = read_json_file('data/', 'structured_pools_v2.json')[:100]
G_v2 = create_graph_from_pools(pool_data_v2)
visualize_graph(G_v2, 'Uniswap V2 Graph')

G_v2 = remove_single_edge_nodes(G_v2)
visualize_graph(G_v2, 'Uniswap V2 2-Connected Graph')

pool_data_v3 = read_json_file('data/', 'structured_pools_v3.json')[:100]
G_v3 = create_graph_from_pools(pool_data_v3)
visualize_graph(G_v3, 'Uniswap V3 Graph')

G_v3 = remove_single_edge_nodes(G_v3)
visualize_graph(G_v3, 'Uniswap V3 2-Connected Nodes')
