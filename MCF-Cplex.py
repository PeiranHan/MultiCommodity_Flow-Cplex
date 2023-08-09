from docplex.mp.model import Model

# Model set up
model = Model(name='MultiCommodityFlow')

# Define the nodes and edges
nodes = ['1', '2', '3', '4', '5', '6', '7']
edges = [('1', '2'),('1', '4'),('1', '3'),('2', '5'),('2', '4'),('5', '7'),('4', '7'),('4', '3'),('3', '6'),('6', '7')]

# Define commodity with origin/destination/demand
commodities = {
    'Commodity1': {'source': '1', 'target': '7', 'demand': 1},
    'Commodity2': {'source': '2', 'target': '6', 'demand':1}
}

# Define the capacity and cost of edge
capacities = {('1', '2'):1,('1', '4'):1,('1', '3'):1,('2', '5'):1,('2', '4'):1,('5', '7'):1,('4', '7'):1,('4', '3'):1,('3', '6'):1,('6', '7'):1}
costs = {('1', '2'):15,('1', '4'):25,('1', '3'):45,('2', '5'):30,('2', '4'):2,('5', '7'):2,('4', '7'):50,('4', '3'):2,('3', '6'):25,('6', '7'):1}

# Variable
flow_vars = {(commodity, edge): model.continuous_var(name=f'Flow_{commodity}_{edge}') for commodity in commodities for edge in edges}

# Objective function
model.minimize(model.sum(flow_vars[commodity, edge] * costs[edge] for commodity in commodities for edge in edges))

# Flow conversation constraint
for node in nodes:
    for commodity, c_info in commodities.items():
        # For origin nodes
        if node == c_info['source']:
            in_edges = [(u, v) for u, v in edges if v == node]
            out_edges = [(u, v) for u, v in edges if u == node]
            model.add_constraint(
                model.sum(flow_vars[commodity, edge] for edge in out_edges)
                - model.sum(flow_vars[commodity, edge] for edge in in_edges) == c_info['demand'],
                ctname=f'FlowConservation_{node}_{commodity}'
            )
        #  For destination nodes
        elif node == c_info['target']:
            in_edges = [(u, v) for u, v in edges if v == node]
            out_edges = [(u, v) for u, v in edges if u == node]
            model.add_constraint(
                model.sum(flow_vars[commodity, edge] for edge in out_edges)
                - model.sum(flow_vars[commodity, edge] for edge in in_edges) == -c_info['demand'],
                ctname=f'FlowConservation_{node}_{commodity}'
            )
        # For intermediate nodes
        else:
            in_edges = [(u, v) for u, v in edges if v == node]
            out_edges = [(u, v) for u, v in edges if u == node]
            model.add_constraint(
                model.sum(flow_vars[commodity, edge] for edge in out_edges)
                - model.sum(flow_vars[commodity, edge] for edge in in_edges) == 0,
                ctname=f'FlowConservation_{node}_{commodity}'
            )

# Capacity constraint
for edge in edges:
    model.add_constraint(
        model.sum(flow_vars[commodity, edge] for commodity in commodities) <= capacities[edge],
        ctname=f'CapacityConstraint_{edge}'
    )

# Solve
model.solve()

# Output
print(f"Total Cost: {model.objective_value:.2f}")
for commodity, c_info in commodities.items():
    for edge in edges:
        if flow_vars[commodity, edge].solution_value > 0:
            print(f"Flow of {commodity} on edge {edge}: {flow_vars[commodity, edge].solution_value:.2f}")
