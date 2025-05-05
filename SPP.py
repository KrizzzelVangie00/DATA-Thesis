# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 09:05:19 2025

@author: icr1t
"""

import networkx as nx
import pandas as pd

df = pd.read_csv("data_E,N.csv")
df.columns = df.columns.str.strip()  

MG = nx.MultiGraph()

for _, row in df.iterrows():
    MG.add_edge(row["Start Node"], row["End Node"], weight=row["Length (km)"], edge_id=row["Edge ID"])

G = nx.Graph()
for u, v, data in MG.edges(data=True):
    weight = data["weight"]
    if G.has_edge(u, v):
        G[u][v]["weight"] = min(G[u][v]["weight"], weight)  # Keep the shortest edge
    else:
        G.add_edge(u, v, weight=weight)

all_shortest_distances = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))

nodes = sorted(G.nodes())  
df_matrix = pd.DataFrame(index=nodes, columns=nodes)

for source in nodes:
    for target in nodes:
        df_matrix.loc[source, target] = all_shortest_distances[source].get(target, float('inf'))  # Inf if no path

output_file = "shortest_paths_matrix.csv"
df_matrix.to_csv(output_file)

print("Shortest Path")
