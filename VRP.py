import pandas as pd
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

# ---------------- Step 1: Define Nodes ----------------
# Use only the 5 nodes that correspond to the distance matrix
nodes = ["N83", "N20", "N60", "N19", "N8"]  # These should match the matrix below

# Define depot and stop nodes
depot_node = "N83"
stops = ["N20", "N60", "N19", "N8"]

# Check that all nodes are valid
assert depot_node in nodes, "Depot node not found in node list."
for stop in stops:
    assert stop in nodes, f"Stop node {stop} not found in node list."

depot_index = nodes.index(depot_node)
stop_indices = [nodes.index(stop) for stop in stops]

distance_matrix_km = [
    [0, 1.851, 1.696, 3.683, 3.668],
    [1.851, 0, 3.427, 2.967, 2.951],
    [1.696, 3.427, 0, 0.461, 0.642],
    [3.683, 2.967, 0.461, 0, 0.182],
    [3.668, 2.951, 0.642, 0.182, 0]
]
distance_matrix = [[int(km * 1000) for km in row] for row in distance_matrix_km]  # Convert to meters

#demands = [0, 10, 15, 8, 10]  # Demand at depot = 0 (no demand), and others have positive demands
demands = [0, 18, 18, 18, 18] 
#demands = [0, 5, 5, 5, 5] 

vehicle_capacity = 18  # Each vehicle can carry up to 18 passengers

def solve_vrp(num_vehicles=4):
    manager = pywrapcp.RoutingIndexManager(len(nodes), num_vehicles, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    # Create a distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, [vehicle_capacity] * num_vehicles, True, "Capacity"
    )

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_params)

    if solution:
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            route_distance = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(nodes[node_index])
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            route.append(nodes[manager.IndexToNode(index)])
            print(f"Route for Vehicle {vehicle_id}: {' -> '.join(route)}")
            print(f"Total distance: {route_distance / 1000:.2f} km\n")
    else:
        print("No solution found.")

solve_vrp()
