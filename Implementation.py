# -*- coding: utf-8 -*-
"""
Created on Mon May  5 01:19:57 2025

@author: Vangie
"""

import pandas as pd
import networkx as nx

df = pd.read_csv("data directions.csv")
df.columns = df.columns.str.strip()

G = nx.DiGraph()

alpha = 1  # Capacity scaling factor


for _, row in df.iterrows():
    u = row['Start Node']
    v = row['End Node']
    length = row['Length (km)']
    speed = row['maxspeed']
    lanes = row['lanes']
    direction = row['Direction'].lower()

    travel_time = length / speed  # hours
    capacity = lanes * speed * alpha

    
    G.add_edge(u, v,
               length=length,
               speed=speed,
               lanes=lanes,
               travel_time=travel_time,
               capacity=capacity)

    if direction == 'bidirectional':
        G.add_edge(v, u,
                   length=length,
                   speed=speed,
                   lanes=lanes,
                   travel_time=travel_time,
                   capacity=capacity)

s, t = "N83", "N43" #source, sink nodes

P_star = nx.dijkstra_path(G, source=s, target=t, weight='travel_time')
print("Shortest Path P*:", P_star)

flow_value, flow_dict = nx.maximum_flow(G, _s=s, _t=t, capacity='capacity')
print("Maximum Flow F* value:", flow_value)

R_star = [P_star]
min_cap = min(G[P_star[i]][P_star[i + 1]]['capacity'] for i in range(len(P_star) - 1))
flow_assigned = min(flow_value, min_cap)

f_r = {}
for i in range(len(P_star) - 1):
    u, v = P_star[i], P_star[i + 1]
    f_r[(u, v)] = flow_assigned

for u, v in f_r:
    flow = f_r[(u, v)]
    capacity = G[u][v]['capacity']
    print(f"Edge ({u}, {v}) Flow: {flow:.2f}, Capacity: {capacity}")
    assert flow <= capacity, f"Flow exceeds capacity on edge ({u}, {v})"

for node in G.nodes():
    if node in [s, t]:
        continue
    inflow = sum(flow_dict[u][node] for u in G.predecessors(node))
    outflow = sum(flow_dict[node][v] for v in G.successors(node))
    print(f"Node {node} Inflow: {inflow}, Outflow: {outflow}")
    assert inflow == outflow, f"Flow conservation violated at node {node}"

print("\n--- Optimized Vehicle Routing Problem Simulation ---")

depot = "N83"
customers = ["N20", "N57", "N51", "N4", "N5", "N81", "N86", "N12", "N22", "N29"]
#demands = [1, 1, 1, 1, 1, 1, 1,1, 1, 1]
#demands = [5, 8, 6, 4, 7, 3, 5 ,8, 4, 6]
#demands = [18, 18, 18, 18, 18, 18, 0, 0, 0, 0]
demands = [18, 18, 18, 18, 18, 18, 18, 18, 18, 18]
vehicle_capacity = 18
vehicle_count = 6

customer_distances = []
for cust in customers:
    try:
        length = nx.dijkstra_path_length(G, depot, cust, weight='length')
        customer_distances.append((cust, length))
    except nx.NetworkXNoPath:
        customer_distances.append((cust, float('inf')))

sorted_customers = sorted(zip(customers, demands), key=lambda x: dict(customer_distances)[x[0]])

routes = [[] for _ in range(vehicle_count)]
loads = [0] * vehicle_count
unassigned_customers = []

for customer, demand in sorted_customers:
    assigned = False
    for i in range(vehicle_count):
        if loads[i] + demand <= vehicle_capacity:
            routes[i].append((customer, demand))
            loads[i] += demand
            assigned = True
            break
    if not assigned:
        unassigned_customers.append((customer, demand))

for i, stops in enumerate(routes):
    if not stops:
        print(f"🚐 Vehicle {i+1} has no assigned route.")
        continue

    path = [depot]
    total_distance = 0
    current_node = depot

    for stop, _ in stops:
        try:
            sub_path = nx.dijkstra_path(G, current_node, stop, weight='length')
            for j in range(len(sub_path) - 1):
                edge_data = G[sub_path[j]][sub_path[j + 1]]
                total_distance += edge_data.get('length', 0)
            path.extend(sub_path[1:])
            current_node = stop
        except nx.NetworkXNoPath:
            print(f"⚠️ Warning: No path from {current_node} to {stop} for vehicle {i+1}.")

    try:
        return_path = nx.dijkstra_path(G, current_node, depot, weight='length')
        for j in range(len(return_path) - 1):
            edge_data = G[return_path[j]][return_path[j + 1]]
            total_distance += edge_data.get('length', 0)
        path.extend(return_path[1:])
    except nx.NetworkXNoPath:
        print(f"⚠️ Warning: Vehicle {i+1} could not return to depot from {current_node}.")

    print(f"\n🚐 Vehicle {i+1} Route: {path}")
    print(f"  Stops: {[stop for stop, _ in stops]}")
    print(f"  Load: {loads[i]} / {vehicle_capacity}")
    print(f"  Total Route Distance (km): {total_distance:.2f}")

if unassigned_customers:
    print("\n⚠️ Unassigned Customers (due to capacity constraints):")
    for customer, demand in unassigned_customers:
        print(f"  {customer} with demand {demand}")
