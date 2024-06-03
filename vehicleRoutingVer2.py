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

# num_vehicles = 3
# max_duration_route = 500

start = time.time()

X_for_kmean, De_for_kmean, X_pairwise = caculate_pairwise(customers_info, depots_info, v=config.V)

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
total_vehicles_need_for_not_allocating = 0
max_vehicles = num_vehicles
num_vehicle_depots_metadata = {} # mảng lưu lại thông tin số lượng xe tương ứng với từng depot
routes_metada_depot_list = []

# Tối ưu route, tính toán chi phí cho tất cả các depot
for depot_index in range(num_depots):
    savings = create_savings(depot_index, 0, depots_customers_metadata, X_pairwise, num_depots)
    routes, routes_metada_depot, _, node_not_assigneds = Clark_Wright_Savings_Solver(
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
        total_demand += routes_metada_depot[route]["total_demand"]
        total_time_serving += routes_metada_depot[route]["total_time_serving"]
    
    routes_metada_depot_list.append(routes_metada_depot)
    
    num_vehicle_depots_metadata[depot_index] = len(routes_metada_depot.keys()) # số lượng route trong 1 depot

    # print("--------- Depot " + str(depot_index) + " ---------")
    # for route in routes_metada_depot.keys():
    #         print("Route: " + str(route))
    #         print("Info: " + str(routes_metada_depot[route]))

    total_vehicles_need_for_not_allocating += num_vehicle_depots_metadata[depot_index]

print("************************************************************")
print("         Final Results Without Allocating Vehicles")
print("************************************************************")
print("Total Demand: " + str(total_demand))
print("Total Distance: " + str(total_distance) + " km")
print("Total Vehicles: " + str(total_vehicles_need_for_not_allocating))
print("Total Time_serving: " + str(total_time_serving) + " minutes = " + str(total_time_serving / 60) + " hours")

total_distance = 0.0
total_demand = 0.0
total_time_serving = 0.0

# Sort num_vehicle_depots_metadata follow by num of routes
num_vehicle_depots_metadata_sorted = sorted(num_vehicle_depots_metadata.items(), key=lambda x:x[1], reverse=True)

num_vehicle_depots_metadata_sorted_origin = {}

for item in num_vehicle_depots_metadata_sorted:
    num_vehicle_depots_metadata_sorted_origin[item[0]] = item[1]

print("Num_depot: " + str(num_depots))
print("Num vehicles: " + str(num_vehicles))

print("--------- So xe uoc tinh ---------") 
# Tuple (a, b) => a là depot_index, b là số xe tương ứng
print(num_vehicle_depots_metadata_sorted)

num_vehicle_depots_metadata_reassigned = caculate_vehicles_for_each_depot_method_1(X_pairwise, num_vehicles, num_vehicle_depots_metadata_sorted, num_vehicle_depots_metadata_sorted_origin)

print("--------- So xe thuc te duoc phan chia ---------") 
# Tuple (a, b) => a là depot_index, b là số xe tương ứng
print(num_vehicle_depots_metadata_reassigned)

# Phân bổ xe cho các route chưa được serving cùng 1 depot
# Serving cho các route có distance total từ nhỏ nhất đến lớn nhất đến khi time last (thời gian còn lại) của vehicle không còn thoả mãn
def allocateVehiclePerDepot(depot_routes_sorted_time, depot_index, num_vehicle_assigned_depot):

    timeLastVehicleDict = {}
    timeRouteDict = {}
    flag_used_route = {}
    route_served = []
    route_not_served = []

    for i, r in enumerate(range(len(depot_routes_sorted_time))):
        timeRouteDict[r] = time_constranst_total(X_pairwise, depot_routes_sorted_time[i], depot_index, num_depots)
        flag_used_route[r] = False
    
    for i, v in enumerate(range(len(depot_routes_sorted_time))):
        t = time_constranst_total(X_pairwise, depot_routes_sorted_time[i], depot_index, num_depots)
        if max_duration_route >= t:
            timeLastVehicleDict[v] = max_duration_route - t
            if i < num_vehicle_assigned_depot:
                flag_used_route[v] = True
        else:
            timeLastVehicleDict[v] = max_duration_route

    finish = False
    count = 0

    while finish != True:

        # print("==== Allocate vehicle iter " + str(count) + " ====")

        finish = True

        list_route_used = []
        list_route_not_used = []

        route_served = []
        route_not_served = []

        for i, r in enumerate(range(len(depot_routes_sorted_time))):
            if flag_used_route[r]:
                list_route_used.append(r)
                # print("Route " + str(r) + " is served has total time: " + str(timeRouteDict[r]))
                route_served.append(depot_routes_sorted_time[r])
            else:
                list_route_not_used.append(r)
                # print("Route " + str(r) + " is not served has total time: " + str(timeRouteDict[r]))
                route_not_served.append(depot_routes_sorted_time[r])

        # for i, v in enumerate(range(num_vehicle_assigned_depot)):
        #     print("Time left for vehicle " + str(v) + ": " + str(timeLastVehicleDict[v]))
        
        for route_used in list_route_used:
            for route_not_used in list_route_not_used:
                if 0 < timeRouteDict[route_not_used] <= timeLastVehicleDict[route_used] and flag_used_route[route_not_used] != True:
                    timeLastVehicleDict[route_used] = timeLastVehicleDict[route_used] - timeRouteDict[route_not_used]
                    flag_used_route[route_not_used] = True
                    finish = False

        count = count + 1

        return timeLastVehicleDict, route_served, route_not_served

# Phân bổ xe cho các route chưa được serving trong cùng một depot, sử dụng các xe lấy từ depot gần nhất
def allocateVehiclePerDepotAfter(depot_routes_sorted_time, depot_index, timeLastVehicleDictCloset):

    timeRouteDict = {}
    flag_used_route = {}
    route_not_served = []
    route_served = []

    for i, r in enumerate(range(len(depot_routes_sorted_time))):
        timeRouteDict[r] = time_constranst_total(X_pairwise, depot_routes_sorted_time[i], depot_index, num_depots)
        flag_used_route[r] = False

    for i, r in enumerate(range(len(depot_routes_sorted_time))):
        t = timeRouteDict[r]
        for v in timeLastVehicleDictCloset.keys():
            if timeLastVehicleDictCloset[v] >= t:
                timeLastVehicleDictCloset[v] = timeLastVehicleDictCloset[v] - t
                flag_used_route[i] = True
                break

    finish = False
    count = 0

    while finish != True:

        finish = True

        list_route_not_used = []
        route_served = []
        route_not_served = []

        for i, r in enumerate(range(len(depot_routes_sorted_time))):
            if not flag_used_route[r]:
                list_route_not_used.append(r) 
                route_not_served.append(depot_routes_sorted_time[r])
            else:
                route_served.append(depot_routes_sorted_time[r])
        
        for route_not_used in list_route_not_used:
            for v in timeLastVehicleDictCloset.keys():
                if timeLastVehicleDictCloset[v] >= timeRouteDict[route_not_used] and flag_used_route[route_not_used] != True:
                    timeLastVehicleDictCloset[v] = timeLastVehicleDictCloset[v] - timeRouteDict[route_not_used]
                    flag_used_route[route_not_used] = True
                    finish = False
                    break

        count = count + 1

        return route_served, route_not_served

timeLastVehicleDictList = []
route_not_served_List = []
route_served_List = []

for depot_index in range(num_depots):

    depot_routes_sorted_time = []

    for route in list(routes_metada_depot_list[depot_index].keys()):
        depot_routes_sorted_time.append(eval(route)[1:-1])

    depot_routes_sorted_time = sorted(depot_routes_sorted_time, key=lambda x:time_constranst_total_for_sort(X_pairwise, x, depot_index, num_depots))

    # print("==== List route of depot " + str(depot_index) + " =====")
    # for route in depot_routes_sorted_time:
    #     print(route)

    for item in num_vehicle_depots_metadata_reassigned:
        if item[0] == depot_index:
            num_vehicle_assigned_depot = item[1]

    timeLastVehicleDict, route_served, route_not_served = allocateVehiclePerDepot(depot_routes_sorted_time, depot_index, num_vehicle_assigned_depot)

    timeLastVehicleDictList.append(timeLastVehicleDict)
    route_not_served_List.append(route_not_served)
    route_served_List.append(route_served)

# Tính toán chi phí cho các route đã được serving
for depot_index, route_served in enumerate(route_served_List):
    for route in route_served:
        route = ["depot_" + str(depot_index)] + route + ["depot_" + str(depot_index)]
        for route_temp in routes_metada_depot_list[depot_index].keys():
            if str(route) == str(route_temp):
                total_distance += routes_metada_depot_list[depot_index][str(route)]["total_distance"]
                total_demand += routes_metada_depot_list[depot_index][str(route)]["total_demand"]
                total_time_serving += routes_metada_depot_list[depot_index][str(route)]["total_time_serving"]

# Đánh dấu xem xe depot nào đang được sử dụng
flag_assigned = {}
for depot_index in range(num_depots):
    flag_assigned[depot_index] = False

closet_depot_info = []
for depot_index in range(num_depots):
    depot_index_closest = get_depot_closet(depot_index, num_depots, X_pairwise, flag_assigned)
    closet_depot_info.append([depot_index, depot_index_closest, distance(X_pairwise[depot_index], X_pairwise[depot_index_closest])])

# sort by distance
closet_depot_info = sorted(closet_depot_info, key=lambda x:x[2])

print("--------- Closet depot mapping ---------")
print(closet_depot_info)

print("************************************************************")
print("          After First Phase Routing Of all Depot")
print("************************************************************")

total_distance_not_served = 0

for depot_index in range(num_depots):
    print("---- Depot " + str(depot_index) + " ----")
    print("Vehicles Available:")
    print(timeLastVehicleDictList[depot_index])
    print("Routes Not Serving:")
    print(route_not_served_List[depot_index])
    for route in route_not_served_List[depot_index]:
        total_distance_not_served += distance_total(X_pairwise, route, depot_index, num_depots)

print("Total Distance Served: " + str(total_distance) + " km")
print("Total Distance not Served: " + str(total_distance_not_served) + " km")
print("Total Distance All: " + str(total_distance_not_served + total_distance) + " km")

print("************************************************************")
print(" Move Vehicles Available from Depot Closet to Depot Current")
print("************************************************************")

total_distance_not_served = 0

# Đánh dấu xem xe depot nào đang được sử dụng
flag_assigned = {}
for depot_index in range(num_depots):
    flag_assigned[depot_index] = False

for item in closet_depot_info:

    depot_index = item[0]

    if len(route_not_served_List[depot_index]) > 0:
        
        # Tìm depot gần nhất với depot hiện tại
        depot_index_closest = get_depot_closet(depot_index, num_depots, X_pairwise, flag_assigned)

        if depot_index_closest != -1:

            # flag_assigned[depot_index] = True
            flag_assigned[depot_index_closest] = True
            
            list_vehicle_in_depot = timeLastVehicleDictList[depot_index]
            list_vehicle_in_depot_closest = timeLastVehicleDictList[depot_index_closest]

            # Sort vehicle by time last
            keys = list(list_vehicle_in_depot_closest.keys())
            values = list(list_vehicle_in_depot_closest.values())
            sorted_value_index = np.argsort(values)
            list_vehicle_in_depot_closest_sorted = {keys[i]: values[i] for i in sorted_value_index}

            # Sort route by distance total
            route_not_served_List_sorted_time = sorted(route_not_served_List[depot_index], key=lambda x:time_constranst_total_for_sort(X_pairwise, x, depot_index, num_depots))
            
            route_served_after, route_not_served_after = allocateVehiclePerDepotAfter(route_not_served_List_sorted_time, depot_index_closest, list_vehicle_in_depot_closest_sorted)

            # Tính toán chi phí routing
            for route in route_served_after:
                route = [depot_index_closest] + route + [depot_index_closest]
                total_distance += distance_total(X_pairwise, route, depot_index_closest, num_depots)
                total_demand += constrant_total(X_pairwise, route[1:-1], depot_index_closest, num_depots)
                total_time_serving += time_constranst_total(X_pairwise, route, depot_index_closest, num_depots)

            print("Routes not serving in Depot " + str(depot_index) + ":")
            print(route_not_served_List[depot_index])
            print("Vehicles Available From Depot " + str(depot_index) + ":")
            print(timeLastVehicleDictList[depot_index])
            print("Vehicles Available From Depot Closet " + str(depot_index_closest) + ":")
            print(timeLastVehicleDictList[depot_index_closest])

            # Tính toán chi phí luân chuyển vehicles
            # Có bao nhiêu key thay đổi thì có bây nhiêu xe được luân chuyển từ depot_index_closest đến depot_index
            # list_diff_key = diffDict(list_vehicle_in_depot_closest, list_vehicle_in_depot_closest_sorted)
            # for key in list_diff_key:
            #     total_distance += D_pairwise[depot_index][depot_index_closest] # khoảng cách từ depot i đến depot j
            #     total_time_serving += caculate_time_travel(D_pairwise[depot_index][depot_index_closest], v)
            #     del list_vehicle_in_depot_closest[key]

            print("Vehicles Available From Depot Closet " + str(depot_index_closest) + " After Routing:")
            print(list_vehicle_in_depot_closest_sorted)
            print("Routes not serving After Routing:")
            print(route_not_served_after)

            timeLastVehicleDictList[depot_index_closest] = list_vehicle_in_depot_closest_sorted # cập nhật time last của các xe ở depot gần nhất
            route_not_served_List[depot_index] = route_not_served_after # cập nhật thông tin các route chưa được serving tại depot_index

            print("************************************************************")
            print("************************************************************")
        else:
            print("Vehicles from Depot closet to " + str(depot_index) + " is busy !!!")
            print("************************************************************")
            print("************************************************************")
    else:
        print("************************************************************")
        print("************************************************************")
        print("No need for allocating vehicle, all routes in depot " + str(depot_index) + " are served !!!")
        print("************************************************************")
        print("************************************************************")

print()
print("************************************************************")
print("          After Two Phase Routing Of all Depot")
print("************************************************************")

count_route_not_serving = 0
total_distance_not_served = 0

for depot_index in range(num_depots):
    print("---- Depot " + str(depot_index) + " ----")
    print("Vehicles Available:")
    print(timeLastVehicleDictList[depot_index])
    print("Routes Not Serving:")
    if len(route_not_served_List[depot_index]) > 0:
        count_route_not_serving += 1
    print(route_not_served_List[depot_index])
    for route in route_not_served_List[depot_index]:
        total_distance_not_served += distance_total(X_pairwise, route, depot_index, num_depots)

print("************************************************************")
print("                      Final Results")
print("************************************************************")
print("Total Demand: " + str(total_demand))
print("Total Distance Served: " + str(total_distance) + " km")
print("Total Distance not Served: " + str(total_distance_not_served) + " km")
print("Total Distance All: " + str(total_distance_not_served + total_distance) + " km")
print("Total Time_serving: " + str(total_time_serving) + " minutes = " + str(total_time_serving / 60) + " hours")
print(time.time() - start)