import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import community as community_louvain
from pyvis.network import Network
import itertools
import os

@st.cache_data(show_spinner=False)
def load_and_preprocess(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=['user_loc', 'fr_loc', 'scaled_sci'])
    df['scaled_sci'] = np.log1p(df['scaled_sci'])
    return df.dropna()

@st.cache_data(show_spinner=False)
def build_full_graph(df: pd.DataFrame) -> nx.Graph:
    G = nx.from_pandas_edgelist(
        df, 'user_loc', 'fr_loc',
        edge_attr='scaled_sci',
        create_using=nx.Graph()
    )
    for u, v in list(G.edges()):
        total_w = df.loc[
            ((df.user_loc == u) & (df.fr_loc == v)) |
            ((df.user_loc == v) & (df.fr_loc == u)),
            'scaled_sci'
        ].sum()
        G[u][v]['weight'] = total_w
    return G

def top_k_subgraph(G: nx.Graph, k: int) -> nx.Graph:
    H = nx.Graph()
    H.add_nodes_from(G.nodes(data=True))
    for n in G.nodes():
        nbrs = sorted(
            G[n].items(),
            key=lambda x: x[1]['weight'],
            reverse=True
        )[:k]
        for v, attr in nbrs:
            H.add_edge(n, v, **attr)
    return H

def weighted_k_core(G: nx.Graph, k: float) -> nx.Graph:
    H = G.copy()
    while True:
        low = [n for n, deg in H.degree(weight='weight') if deg < k]
        if not low:
            break
        H.remove_nodes_from(low)
    return H

@st.cache_data(show_spinner=False)
def detect_and_layout(_G: nx.Graph) -> nx.Graph:
    """
    Only detect communities here. Layout will be handled by Vis.js physics.
    """
    G = _G
    partition = community_louvain.best_partition(G, weight='weight')
    nx.set_node_attributes(G, partition, 'community')
    return G

def make_pyvis_html(G: nx.Graph) -> str:
    """Generate an interactive PyVis HTML with live physics."""
    net = Network(
        height='750px',
        width='100%',
        directed=False,
        notebook=False
    )
    
    net.barnes_hut(
        gravity=-20000,
        central_gravity=0.3,
        spring_length=50,
        spring_strength=0.1,
        damping=0.9,
        overlap=0
    )

    palette = itertools.cycle([
        '#e6194b','#3cb44b','#ffe119','#4363d8','#f58231',
        '#911eb4','#46f0f0','#f032e6','#bcf60c','#fabebe'
    ])
    comms = set(nx.get_node_attributes(G, 'community').values())
    colors = {c: next(palette) for c in comms}

    for node, data in G.nodes(data=True):
        strength = G.degree(node, weight='weight')
        net.add_node(
            node,
            label=node,
            font={
                "size": 50,
            },
            title=f"Strength: {strength:.2f}",
            color=colors[data['community']],
            size=(5 + np.log1p(strength))
        )

    for u, v, data in G.edges(data=True):
        net.add_edge(
            u, v,
            value=data['weight'],
            title=f"Weight: {data['weight']:.2f}"
        )

    net.show_buttons(filter_=['physics','layout'])
    return net.generate_html()

def get_sci_network_visual():
    st.title("Sparse‑View SCI Network with Live Physics")

    st.markdown("""
    ## Network Visualization with Louvain, K-Core, and Top-K Algorithms

    This visualization employs three key graph algorithms—**Louvain Community Detection**, **K-Core Decomposition**, and **Top-K Subgraph Extraction**—to analyze and display the structure of a network based on trade data.

    ### Why is this important?

    These algorithms help uncover hidden patterns and structures within complex networks:

    - **Louvain Community Detection**: Identifies groups of nodes (countries) that are more densely connected to each other than to the rest of the network, revealing natural clusters or communities.

    - **K-Core Decomposition**: Finds the most connected subgraphs by removing nodes with fewer than 'k' connections, helping to highlight the core structure of the network.

    - **Top-K Subgraph Extraction**: Focuses on the 'k' most significant connections for each node, allowing for a simplified view of the network's most influential relationships.

    By applying these algorithms, we can gain insights into the most influential countries in trade and how they are interconnected.

    ### How to read the visualization:

    - **Nodes**: Represent countries involved in trade.

    - **Edges**: Represent trade relationships between countries, with thickness indicating the strength of the trade connection.

    - **Colors**: Indicate different communities identified by the Louvain algorithm.

    - **Interactivity**: Hover over nodes and edges to view detailed information about each country and trade relationship.

    This interactive visualization allows users to explore the global trade network, identify key players, and understand the structure of international trade relationships.

    """)

    data_path = os.path.join('data','Country_Names_SCI.csv')
    df = load_and_preprocess(data_path)

    top_k    = st.slider("Keep Top‑K edges per node", 1, 20, 5)

    G_full   = build_full_graph(df)
    G_sparse = top_k_subgraph(G_full, top_k)

    G_comm = detect_and_layout(G_sparse)
    html   = make_pyvis_html(G_comm)

    st.components.v1.html(html, height=800, scrolling=True)
