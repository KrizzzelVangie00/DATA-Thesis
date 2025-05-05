# -*- coding: utf-8 -*-
"""
Created on Thu Apr  3 11:28:00 2025

@author: Vangie
"""

import networkx as nx
import pandas as pd

def add_edges_from_csv(G, csv_file):
    df = pd.read_csv(csv_file)
    
    df["Start Node"] = df["Start Node "].astype(str)  
    df["End Node"] = df["End Node"].astype(str)

    for _, row in df.iterrows():
        u, v = row['Start Node '], row['End Node']
        lanes, maxspeed, length = row['lanes'], row['maxspeed'], row['Length (km)']
        
        capacity = (lanes * maxspeed) / length  

        G.add_edge(u, v, capacity=capacity)
        
        if row['Direction'] == 'Bidirectional':  
            G.add_edge(v, u, capacity=capacity)

def compute_max_flow(G, source, sink):
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    
    print(f"\nThe maximum possible flow from {source} to {sink} is {flow_value:.2f} vehicles/hour")

    return flow_value, flow_dict

def print_ordered_flow(flow_dict, source, sink):
    visited = set()
    queue = [source]

    print("\n Flow Distribution:")
    
    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor, flow in flow_dict[node].items():
            if flow > 0:  # Only print edges with actual flow
                print(f"Edge ({node} → {neighbor}): {flow:.2f} vehicles/hour")
                queue.append(neighbor)  # Continue BFS traversal


if __name__ == "__main__":
    csv_file = "data directions.csv"  
    
    G = nx.DiGraph()
    
    add_edges_from_csv(G, csv_file)
    
    source_node = "N83"
    sink_node = "N60"
    
    max_flow_value, flow_dict = compute_max_flow(G, source_node, sink_node)
    
    print_ordered_flow(flow_dict, source_node, sink_node)
