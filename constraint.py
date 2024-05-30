from utils import *
import config
# Tính toán các đại lượng constrant (ở đây đang xét đến demand)
def constrant_total(X_pairwise, route, depot_index, num_depots):
    constrant_total = 0
    for node in route:
        if node == "depot_" + str(depot_index):
            constrant_total += X_pairwise[depot_index][2] # tính demand của node depot_index
        else:
            constrant_total += X_pairwise[node+num_depots][2] # tính demand của node customers
    return constrant_total

# Time serving constranst
def time_constranst_total(X_pairwise, routeNew, depot_index, num_depots):
    total_time = 0.0
    routeNewTemp = routeNew
    if routeNew[0] == depot_index and routeNew[-1] == depot_index and len(routeNew) > 1:
        routeNewTemp = routeNew[1:-1]
    for i in range(len(routeNewTemp)):
        if routeNewTemp[i] != depot_index and i + 1 <= len(routeNewTemp) - 1:
            # total_time += T_pairwise[routeNewTemp[i] + num_depots][routeNewTemp[i + 1] + num_depots] + X_pairwise[routeNewTemp[i] + num_depots][3]
            total_time += caculate_time_travel(distance(X_pairwise[routeNewTemp[i] + num_depots], X_pairwise[routeNewTemp[i + 1] + num_depots]), config.V) + X_pairwise[routeNewTemp[i] + num_depots][3]
        else:
            total_time += X_pairwise[routeNewTemp[i] + num_depots][3]
    # total_time += T_pairwise[depot_index][routeNewTemp[0] + num_depots]
    total_time += caculate_time_travel(distance(X_pairwise[depot_index], X_pairwise[routeNewTemp[0] + num_depots]), config.V)
    # total_time += T_pairwise[depot_index][routeNewTemp[-1] + num_depots]
    total_time += caculate_time_travel(distance(X_pairwise[depot_index], X_pairwise[routeNewTemp[-1] + num_depots]), config.V)
    return total_time