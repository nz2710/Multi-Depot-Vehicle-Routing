from pyvrp import Model
import matplotlib.pyplot as plt
from pyvrp.plotting import plot_coordinates, plot_result
from dataParser import customers_info, depots_info
from pyvrp.stop import MaxRuntime
import math
import numpy as np
from haversine import haversine
# Tạo mảng dữ liệu depots
def distance(node1, node2):
    return haversine((node1[0], node1[1]), (node2[0], node2[1]))

De = []
for depot_info in depots_info:
    depot_info = " ".join(depot_info.split())
    x = float(depot_info.split()[1])
    y = float(depot_info.split()[2])
    service_time = float(depot_info.split()[3])
    demand = float(depot_info.split()[4])
    De.append([x, y])
De = np.array(De)

X = []
for customer_info in customers_info:
    customer_info = " ".join(customer_info.split())
    x = float(customer_info.split()[1])
    y = float(customer_info.split()[2])
    service_time = float(customer_info.split()[3])
    demand = float(customer_info.split()[4])
    X.append([x, y,service_time,demand])
X = np.array(X)

DeX = []
for depot_info in depots_info:
    depot_info = " ".join(depot_info.split())
    x = float(depot_info.split()[1])
    y = float(depot_info.split()[2])
    service_time = float(depot_info.split()[3])
    demand = float(depot_info.split()[4])
    DeX.append([x, y, service_time, demand])
for customer_info in customers_info:
    customer_info = " ".join(customer_info.split())
    x = float(customer_info.split()[1])
    y = float(customer_info.split()[2])
    service_time = float(customer_info.split()[3])
    demand = float(customer_info.split()[4])
    DeX.append([x, y,service_time,demand])
DeX = np.array(DeX)
num_nodes = len(DeX)
# distance=np.sqrt((DeX.[0][1] - .x)**2 + (frm.y - to.y)**2)
# print(DeX[0][0])
# print(num_nodes)
T_pairwise = np.zeros((num_nodes, num_nodes))
for i in range(num_nodes):
    for j in range(num_nodes):
        T_pairwise[i][j] = distance(DeX[i], DeX[j])
T_pairwise = np.array(T_pairwise)
# print(T_pairwise)

# print(num_nodes)
m = Model()
depots = [
    m.add_depot(
        x=De[idx][0],
        y=De[idx][1],
    )
    for idx in range(len(De))
]
for depot in depots:
    # Two vehicles at each of the depots, with maximum route durations
    # of 30.
    m.add_vehicle_type(20, depot=depot, max_duration=600, capacity=500)
clients = [
    m.add_client(
        x=X[idx][0],
        y=X[idx][1],
        service_duration=X[idx][2],
        delivery=X[idx][3]
    )
    for idx in range(len(X))
]
locations = depots + clients
# print(list(enumerate(locations)))
for frm_idx, frm in enumerate(locations):
    for to_idx, to in enumerate(locations):
        distance = haversine((frm.x, frm.y), (to.x, to.y))
        duration = T_pairwise[frm_idx][to_idx]
        m.add_edge(frm, to, distance=distance, duration=duration)
# _, ax = plt.subplots(figsize=(12, 8))
# plot_coordinates(m.data(), ax=ax)        
res = m.solve(stop=MaxRuntime(400), display=True)  # one second
print(res)
solution = res.best
routes = solution.routes()
for route in routes:
    print(route.depot(),route.distance(), route.service_duration(), route.delivery())
# fig = plt.figure(figsize=(12, 8))
# plot_result(res,m.data(), fig=fig)
# plt.tight_layout()
# plt.show()