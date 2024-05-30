import numpy as np
from dataParser import customers_info, depots_info, num_vehicles, num_depots, max_duration_route, vehicle_capacity
from kmeanClustering import KmeanMVRP
import config
from utils import *
from constraint import *
from cw import *
import time

np.random.seed(config.SEED_NUMBER)

# Time đơn vị tính theo phút
# Distance đơn vị tính theo km
# Vận tốc v tính theo km/h

# num_vehicles = 70
# max_duration_route = 500

# with open("pickle/X_for_kmean.pkl", "rb") as f:
#     X_for_kmean = pickle.load(f)

# with open("pickle/De_for_kmean.pkl", "rb") as f:
#     De_for_kmean = pickle.load(f)

# with open("pickle/X_pairwise.pkl", "rb") as f:
#     X_pairwise = pickle.load(f)

# with open("pickle/D_pairwise.pkl", "rb") as f:
#     D_pairwise = pickle.load(f)

# with open("pickle/T_pairwise.pkl", "rb") as f:
#     T_pairwise = pickle.load(f)

start = time.time()

X_for_kmean, De_for_kmean, X_pairwise = caculate_pairwise(customers_info, depots_info, v=config.V)

# with open("pickle/X_for_kmean.pkl", "wb") as f:
#     pickle.dump(X_for_kmean, f)

# with open("pickle/De_for_kmean.pkl", "wb") as f:
#     pickle.dump(De_for_kmean, f)

# with open("pickle/X_pairwise.pkl", "wb") as f:
#     pickle.dump(X_pairwise, f)

# with open("pickle/D_pairwise.pkl", "wb") as f:
#     pickle.dump(D_pairwise, f)

# with open("pickle/T_pairwise.pkl", "wb") as f:
#     pickle.dump(T_pairwise, f)

v = config.V

# Clustering
app = KmeanMVRP()

centroids_metadata_sorted, depots_centroids_metadata, depots_customers_metadata = app.kmean_assign_depots_closest_centroids(
                                                                                    X=X_for_kmean, 
                                                                                    De=De_for_kmean, 
                                                                                    num_depots=num_depots, 
                                                                                    num_clusters=num_depots
                                                                                )

total_distance = 0.0
total_demand = 0.0
total_time_serving = 0.0
total_distance_route_has_one_node = 0.0
max_vehicles = num_vehicles
num_vehicle_depots_metadata = {} # mảng lưu lại thông tin số lượng xe tương ứng với từng depot
routes_metada_depot_list = []
node_not_assigneds_mapping = {}
node_not_assigneds_mapping_cw = {}

# Tối ưu route, tính toán chi phí cho tất cả các depot
for depot_index in range(num_depots):
    print("---- Depot " + str(depot_index) + ' ----')
    savings = create_savings(depot_index, 0, depots_customers_metadata, X_pairwise, num_depots)
    routes, routes_metada_depot, node_list_origin, node_not_assigneds = Clark_Wright_Savings_Solver(
                                X_pairwise, 
                                savings, 
                                depot_index, 
                                0, 
                                depots_customers_metadata, 
                                vehicle_capacity,
                                num_depots,
                                max_vehicles,
                                max_duration_route,
                                v
                            )
    
    for route in routes_metada_depot.keys():
        print(routes_metada_depot[route])
        if len(node_not_assigneds) == 0:
            print(route)
            total_distance += routes_metada_depot[route]["total_distance"]
            total_demand += routes_metada_depot[route]["total_demand"]
            total_time_serving += routes_metada_depot[route]["total_time_serving"]
            total_distance_route_has_one_node += routes_metada_depot[route]["total_distance_route_has_one_node"]
    
    routes_metada_depot_list.append(routes_metada_depot)
    
    num_vehicle_depots_metadata[depot_index] = len(routes_metada_depot.keys()) # số lượng route trong 1 depot

    if len(node_not_assigneds) > 0:
        node_not_assigneds_mapping[depot_index] = node_list_origin
        node_not_assigneds_mapping_cw[depot_index] = node_not_assigneds

print("************************************************************")
print("         Post Processing nodes not serving")
print("************************************************************")
print("---- Depot customer infor before post processing ----")
print(node_not_assigneds_mapping_cw)
# Xử lý các nodes chưa được serving => phân cụm và routing lại các depots chứa các nodes chưa được serving, tạm thời chưa dùng while
if len(node_not_assigneds_mapping.keys()) > 0:

    num_depots_after_cw = len(node_not_assigneds_mapping_cw.keys())
    X_for_kmean_after_cw = []
    De_for_kmean_after_cw = []
    mapping_after_cw = {}
    mapping_depot_index_cw = {}
    for index, depot_index in enumerate(node_not_assigneds_mapping_cw.keys()):
        mapping_depot_index_cw[index] = depot_index
        De_for_kmean_after_cw.append(De_for_kmean[depot_index])
        for point in node_not_assigneds_mapping_cw[depot_index]:
            X_for_kmean_after_cw.append(X_for_kmean[point])
            mapping_after_cw[len(X_for_kmean_after_cw) - 1] = point

    X_for_kmean_after_cw = np.array(X_for_kmean_after_cw)
    De_for_kmean_after_cw = np.array(De_for_kmean_after_cw)

    app = KmeanMVRP()

    centroids_metadata_sorted_after_cw, depots_centroids_metadata_after_cw, depots_customers_metadata_after_cw = app.kmean_assign_depots_closest_centroids(
                                                                                        X=X_for_kmean_after_cw, 
                                                                                        De=De_for_kmean_after_cw, 
                                                                                        num_depots=num_depots_after_cw, 
                                                                                        num_clusters=num_depots_after_cw,
                                                                                        max_iter=1000
                                                                                    )
    # print(depots_customers_metadata_after_cw)
    
    depots_customers_metadata_after_mapping_cw = {}
    for depot_index in depots_customers_metadata_after_cw.keys():
        depots_customers_metadata_after_mapping_cw[mapping_depot_index_cw[depot_index]] = depots_customers_metadata_after_cw[depot_index]
        for index, point in enumerate(depots_customers_metadata_after_cw[depot_index][0]):
            # print(mapping_after_cw[point])
            # print(depots_customers_metadata_after_mapping_cw)
            depots_customers_metadata_after_mapping_cw[mapping_depot_index_cw[depot_index]][0][index] = mapping_after_cw[point]

    num_depots_after = len(node_not_assigneds_mapping.keys())
    X_for_kmean_after = []
    De_for_kmean_after = []
    mapping_after = {}
    mapping_depot_index = {}
    for index, depot_index in enumerate(node_not_assigneds_mapping.keys()):
        mapping_depot_index[index] = depot_index
        De_for_kmean_after.append(De_for_kmean[depot_index])
        for point in node_not_assigneds_mapping[depot_index]:
            X_for_kmean_after.append(X_for_kmean[point])
            mapping_after[len(X_for_kmean_after) - 1] = point

    X_for_kmean_after = np.array(X_for_kmean_after)
    De_for_kmean_after = np.array(De_for_kmean_after)

    app = KmeanMVRP()

    centroids_metadata_sorted_after, depots_centroids_metadata_after, depots_customers_metadata_after = app.kmean_assign_depots_closest_centroids(
                                                                                        X=X_for_kmean_after, 
                                                                                        De=De_for_kmean_after, 
                                                                                        num_depots=num_depots_after, 
                                                                                        num_clusters=num_depots_after,
                                                                                        max_iter=1000
                                                                                    )
    # print(len(De_for_kmean_after))
    depots_customers_metadata_after_mapping = {}
    for depot_index in depots_customers_metadata_after.keys():
        depots_customers_metadata_after_mapping[mapping_depot_index[depot_index]] = depots_customers_metadata_after[depot_index]
        for index, point in enumerate(depots_customers_metadata_after[depot_index][0]):
            depots_customers_metadata_after_mapping[mapping_depot_index[depot_index]][0][index] = mapping_after[point]
    
    print("---- Depot customer infor after post processing ----")
    print(depots_customers_metadata_after_mapping)
    print(depots_customers_metadata_after_mapping_cw)

    for depot_index in depots_customers_metadata_after_mapping.keys():
        depots_customers_metadata_after_mapping[depot_index][0] += depots_customers_metadata_after_mapping_cw[depot_index][0]
    
    for depot_index in range(num_depots_after):
        print("---- Depot " + str(mapping_depot_index[depot_index]) + ' ----')
        savings = create_savings(mapping_depot_index[depot_index], 0, depots_customers_metadata_after_mapping, X_pairwise, num_depots)
        routes, routes_metada_depot, node_list_origin, node_not_assigneds = Clark_Wright_Savings_Solver(
                                    X_pairwise, 
                                    savings, 
                                    mapping_depot_index[depot_index], 
                                    0, 
                                    depots_customers_metadata_after_mapping, 
                                    vehicle_capacity,
                                    num_depots,
                                    max_vehicles,
                                    max_duration_route,
                                    v
                                )
        for route in routes_metada_depot.keys():
            print(routes_metada_depot[route])
            if len(node_not_assigneds) == 0:
                print(route)
                total_distance += routes_metada_depot[route]["total_distance"]
                total_demand += routes_metada_depot[route]["total_demand"]
                total_time_serving += routes_metada_depot[route]["total_time_serving"]
                total_distance_route_has_one_node += routes_metada_depot[route]["total_distance_route_has_one_node"]

        routes_metada_depot_list.append(routes_metada_depot)
    
        num_vehicle_depots_metadata[mapping_depot_index[depot_index]] = len(routes_metada_depot.keys()) # số lượng route trong 1 depot

        if len(node_not_assigneds) > 0:
            print("Need a while loop to solve !!!")

print("************************************************************")
print("         Final Results Without Allocating Vehicles")
print("************************************************************")
print("Total Demand: " + str(total_demand))
print("Total Distance: " + str(total_distance) + " km")
print("Total Distance has one node: " + str(total_distance_route_has_one_node) + " km")
print("Total Time_serving: " + str(total_time_serving) + " minutes = " + str(total_time_serving / 60) + " hours")

print(time.time() - start)

# Check lại xem tính toán distance đã đúng chưa
route = [2, 261, 140, 274, 48, 204, 179, 231, 41, 28, 2]
print(distance_total(X_pairwise, route, depot_index=2, num_depots=num_depots))