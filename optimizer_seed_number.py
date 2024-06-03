import numpy as np
# np.seterr(divide='ignore', invalid='ignore')
from dataParser import customers_info, depots_info, num_depots, max_duration_route, vehicle_capacity, num_vehicles
from kmeanClustering import KmeanMVRP
import config
from utils import *
from constraint import *
from cw import *
from tqdm import tqdm
from multiprocessing import Pool
import pickle
import time

# Time đơn vị tính theo phút
# Distance đơn vị tính theo km
# Vận tốc v tính theo km/h

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

max_vehicles = num_vehicles
X_for_kmean, De_for_kmean, X_pairwise = caculate_pairwise(customers_info, depots_info, v=config.V)

v = config.V

def getTotalDistance(num):
    
    np.random.seed(num)
    
    # Clustering
    app = KmeanMVRP()

    _, _, depots_customers_metadata = app.kmean_assign_depots_closest_centroids(
                                        X=X_for_kmean, 
                                        De=De_for_kmean, 
                                        num_depots=num_depots, 
                                        num_clusters=num_depots
                                    )

    total_distance = 0.0

    # Tối ưu route, tính toán chi phí cho tất cả các depot
    for depot_index in range(num_depots):
        savings = create_savings(depot_index, 0, depots_customers_metadata, X_pairwise, num_depots)
        _, routes_metada_depot, _, _ = Clark_Wright_Savings_Solver(
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
            total_distance += routes_metada_depot[route]["total_distance"]

    return num, total_distance

if __name__ == "__main__":

    List_total_distance = []

    List_nums = list(range(0, 100))

    # for num in tqdm(List_nums):
    #     List_total_distance.append(getTotalDistance(num))
    
    with Pool(processes=4) as p:
        List_total_distance = list(tqdm(p.imap(getTotalDistance, List_nums), total=len(List_nums)))

    List_total_distance = sorted(List_total_distance, key=lambda kv: kv[1])

    index_min_total_distance = List_total_distance[0][0]

    with open("optimize_seed.txt", "w") as fw:
        fw.write(str(index_min_total_distance))

    print("Optimized seed number: " + str(index_min_total_distance))