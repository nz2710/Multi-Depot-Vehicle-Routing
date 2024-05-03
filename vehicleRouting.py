import numpy as np
from dataParser import customers_info, depots_info, m, n, t
from kmeanClustering import KmeanMVRP
import math

# Time đơn vị tính theo phút
# Distance đơn vị tính theo km
# Vận tốc v tính theo km/h

num_vehicles, vehicle_capacity, max_duration_route, v = 100, 180, 450, 80

# Hàm tính khoảng cách eclid
def distance(node1, node2):
    square = math.pow((node1[0] - node2[0]), 2) + math.pow((node1[1] - node2[1]), 2)
    return math.sqrt(square)

# Hàm tính thời gian
def caculate_time_travel(distance, v):
    return (distance / v) * 60

# Tạo mảng dữ liệu khoảng cách giữa tất cả các nodes
def caculate_pairwise_distance(customers_info, depots_info):

    num_customers = len(customers_info)

    num_depots = len(depots_info)

    X_pairwise = []

    for depot_info in depots_info:
        depot_info = " ".join(depot_info.split())
        x = float(depot_info.split()[1])
        y = float(depot_info.split()[2])
        d = float(depot_info.split()[4])
        t = float(depot_info.split()[3])
        X_pairwise.append([x, y, d, t])
    
    for customer_info in customers_info:
        customer_info = " ".join(customer_info.split())
        x = float(customer_info.split()[1])
        y = float(customer_info.split()[2])
        d = float(customer_info.split()[4])
        t = float(customer_info.split()[3])
        X_pairwise.append([x, y, d, t])

    num_nodes = len(X_pairwise)

    D_pairwise = np.zeros((num_nodes, num_nodes))

    T_pairwise = np.zeros((num_nodes, num_nodes))

    for i in range(num_nodes):
        for j in range(num_nodes):
            D_pairwise[i][j] = distance(X_pairwise[i], X_pairwise[j])
            T_pairwise[i][j] = caculate_time_travel(D_pairwise[i][j], v)
    
    return D_pairwise, T_pairwise, num_customers, num_depots, X_pairwise

def create_savings(depot_index, cluster_index, depots_customers_metadata, D_pairwise, num_depots):
    savings = dict()
    for i in depots_customers_metadata[depot_index][cluster_index]:
        for j in depots_customers_metadata[depot_index][cluster_index]:
            if i != j:            
                max_start = max(i, j)
                min_end = min(i, j)
                key = '[' + str(max_start) + ',' + str(min_end) + ']'
                savings[key] = D_pairwise[depot_index][i+num_depots] + D_pairwise[depot_index][j+num_depots] - D_pairwise[i+num_depots][j+num_depots]
    return savings

app = KmeanMVRP()

centroids_metadata_sorted, depots_centroids_metadata, depots_customers_metadata = app.kmean_assign_depots_closest_centroids(
                                                                                    customers_info=customers_info, 
                                                                                    depots_info=depots_info, 
                                                                                    num_depots=t, 
                                                                                    num_clusters=t
                                                                                )

D_pairwise, T_pairwise, num_customers, num_depots, X_pairwise = caculate_pairwise_distance(customers_info, depots_info)

# convert '[1, 2]' into list [1, 2]
def get_link(link):
    link = link.replace('[', '')
    link = link.replace(']', '')
    nodes = link.split(',')
    return [int(nodes[0]), int(nodes[1])]

# Kiểm tra xem một nodeI có nằm trong routeR hay không
def is_node_interior(nodeI, routeR):
    try:
        indexNode = routeR.index(nodeI)
        if indexNode == 0 or indexNode == (len(routeR) - 1):
            return False
        return True
    except:
        return False

# Merge 2 route sẵn có với nhau thông qua link (i, j)
def merge(route_r, route_R, link_ij):

    if route_r.index(link_ij[0]) != (len(route_r) - 1):
        route_r.reverse()
    
    if route_R.index(link_ij[1]) != 0:
        route_R.reverse()
        
    return route_r + route_R

# Tính toán các đại lượng constrant (ở đây đang xét đến demand)
def constrant_total(X_pairwise, route, num_depots):
    constrant_total = 0
    for node in route:
        if node == "depot_" + str(depot_index):
            constrant_total += X_pairwise[depot_index][2] # tính demand của node depot_index
        else:
            constrant_total += X_pairwise[node+num_depots][2] # tính demand của node customers
    return constrant_total

# Time serving constranst
def time_constranst_total(T_pairwise, routeNew, depot_index, num_depots):
    total_time = 0.0
    for i in range(len(routeNew) - 1):
        total_time += T_pairwise[routeNew[i] + num_depots][routeNew[i + 1] + num_depots] + X_pairwise[routeNew[i] + num_depots][3]
    total_time += T_pairwise[depot_index][routeNew[0] + num_depots]
    total_time += T_pairwise[depot_index][routeNew[-1] + num_depots]
    return total_time

# Total distance
def distance_total(D_pairwise, routeNew, depot_index, num_depots):
    total_distance = 0.0
    for i in range(len(routeNew) - 1):
        total_distance += D_pairwise[routeNew[i] + num_depots][routeNew[i + 1] + num_depots]
    total_distance += D_pairwise[depot_index][routeNew[0] + num_depots]
    total_distance += D_pairwise[depot_index][routeNew[-1] + num_depots]
    return total_distance

# Bước 3 thuật toán
def link_and_route(link, routes):

    node_in_route = [] # mảng lưu danh sách các node thuộc link nếu node này đã được assign vào một route hiện có
    index_route = [-1, -1] # mảng index lưu index route mà các node trong link thuộc vào (nếu có)
    overlap_route = 0 # = 1 nếu cả 2 node trong link đều được assign vào cùng 1 route
    count_node_in_link_belong_exist_route = 0
    
    for route in routes:
        for node in link:
            try:
                route.index(node)
                index_route[count_node_in_link_belong_exist_route] = routes.index(route)
                node_in_route.append(node)
                count_node_in_link_belong_exist_route += 1
            except:
                pass
                
    if index_route[0] == index_route[1]:
        overlap_route = 1
    else:
        overlap_route = 0
        
    return node_in_route, count_node_in_link_belong_exist_route, index_route, overlap_route

def Clark_Wright_Savings_Solver(X_pairwise,
                                T_pairwise, 
                                savings, 
                                depot_index, 
                                cluster_index, 
                                depots_customers_metadata, 
                                vehicle_capacity,
                                num_vehicles, 
                                num_depots
    ):

    routes = [] # mảng lưu lại các route => target của thuật toán

    routes_metada_depot = {}

    # Biến quyết định khi nào dừng thuật toán
    continue_algorithm = True

    # Danh sách các nodes, không bao gồm depot
    node_list = depots_customers_metadata[depot_index][cluster_index]

    # Danh sách các nodes chưa được assign
    node_not_assgineds = []

    # Duyệt lần lượt các link trong mảng savings
    for link in savings.keys():

        if continue_algorithm:

            link = get_link(link)
            node_in_route, count_node_in_link_belong_exist_route, index_route, overlap_route = link_and_route(link, routes)

            # Nếu cả 2 node i, j đều chưa thuộc một route nào => TH1
            if count_node_in_link_belong_exist_route == 0:
                if constrant_total(X_pairwise, link, num_depots) <= vehicle_capacity \
                and len(routes) < num_vehicles \
                and time_constranst_total(T_pairwise, link, depot_index, num_depots) <= max_duration_route:
                    routes.append(link)
                    node_list.remove(link[0])
                    node_list.remove(link[1])

            # Nếu một trong hai node i, j thuộc 1 route nào đó sẵn có => TH2    
            elif count_node_in_link_belong_exist_route == 1:

                n_route = node_in_route[0]
                i_route = index_route[0]
                position = routes[i_route].index(n_route)
                link_temp = link.copy()
                link_temp.remove(n_route)
                node = link_temp[0]

                is_node_interior_flag = (not is_node_interior(n_route, routes[i_route]))
                is_satisfy_constrant = (constrant_total(X_pairwise, routes[i_route] + [node], num_depots) <= vehicle_capacity)

                if is_node_interior_flag:
                    if is_satisfy_constrant:
                        if position == 0:
                            routes[i_route].insert(0, node)
                            if time_constranst_total(T_pairwise, routes[i_route], depot_index, num_depots) <= max_duration_route:
                                node_list.remove(node)
                            else:
                                routes[i_route] = routes[i_route][1:]
                        else:
                            routes[i_route].append(node)
                            if time_constranst_total(T_pairwise, routes[i_route], depot_index, num_depots) <= max_duration_route:
                                node_list.remove(node)
                            else:
                                routes[i_route] = routes[i_route][:-1]
                    else:
                        continue
                else:
                    continue
            
            # TH3 thuật toán
                    
            else:

                if overlap_route == 0:

                    is_node_interior_flag1 = (not is_node_interior(node_in_route[0], routes[index_route[0]]))
                    is_node_interior_flag2 = (not is_node_interior(node_in_route[1], routes[index_route[1]]))
                    is_satisfy_constrant = (constrant_total(X_pairwise, routes[index_route[0]] + routes[index_route[1]], num_depots) <= vehicle_capacity)

                    if is_node_interior_flag1 and is_node_interior_flag2:
                        if is_satisfy_constrant:
                            route_temp = merge(routes[index_route[0]], routes[index_route[1]], node_in_route)
                            if time_constranst_total(T_pairwise, route_temp, depot_index, num_depots) <= max_duration_route:
                                temp1 = routes[index_route[0]]
                                temp2 = routes[index_route[1]]
                                routes.remove(temp1)
                                routes.remove(temp2)
                                routes.append(route_temp)
                                try:
                                    node_list.remove(link[0])
                                    node_list.remove(link[1])
                                except:
                                    pass
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
        else:
            break

        if len(node_list) > 0:
            continue_algorithm = True
        else:
            continue_algorithm = False

    # Nếu còn bất kỳ node nào chưa được assign route, 
    # tạo 1 route mới chỉ bao gồm 1 node đó (nếu có constranst về số xe, phải kiểm tra thêm điều kiện)
    for node_not_assgined in node_list:
        if len(routes) < num_vehicles \
        and caculate_time_travel(T_pairwise[depot_index][node_not_assgined + num_depots], v) <= max_duration_route:
            routes.append([node_not_assgined])
        else:
            node_not_assgineds.append(node_not_assgined)

    # Thêm node depot vào các routes tìm được
    for route in routes:
        route_temp = route
        route = ["depot_" + str(depot_index)] + route + ["depot_" + str(depot_index)]
        routes_metada_depot[str(route)] = {
                                            "total_demand": constrant_total(X_pairwise, route, num_depots), 
                                            "total_time_serving": time_constranst_total(T_pairwise, route_temp, depot_index, num_depots),
                                            "total_distance": distance_total(D_pairwise, route_temp, depot_index, num_depots)
                                        }

    if len(node_not_assgineds) > 0:
        print("Error: Không thoả mãn ràng buộc num_vehicles hoặc max_duration_route !!!")
        return [], {}, node_not_assgineds

    return routes, routes_metada_depot, node_not_assgineds

total_distance = 0.0
total_demand = 0.0
total_time_serving = 0.0
num_vehicle_depots_metadata = {} # mảng lưu lại thông tin số lượng xe tương ứng với từng depot

# Tối ưu route, tính toán chi phí cho tất cả các depot
for depot_index in range(num_depots):
    savings = create_savings(depot_index, 0, depots_customers_metadata, D_pairwise, num_depots)
    routes, routes_metada_depot, node_not_assgineds = Clark_Wright_Savings_Solver(
                                X_pairwise, 
                                T_pairwise, 
                                savings, 
                                depot_index, 
                                0, 
                                depots_customers_metadata, 
                                vehicle_capacity,
                                num_vehicles, 
                                num_depots
                            )
    for route in routes_metada_depot.keys():
        total_distance += routes_metada_depot[route]["total_distance"]
        total_demand += routes_metada_depot[route]["total_demand"]
        total_time_serving += routes_metada_depot[route]["total_time_serving"]
    
    num_vehicle_depots_metadata[depot_index] = len(routes_metada_depot.keys()) # số lượng route trong 1 depot

    print("--------- Depot " + str(depot_index) + " ---------")
    for route in routes_metada_depot.keys():
        print("Route: " + str(route))
        print("Info: " + str(routes_metada_depot[route]))

# Sort num_vehicle_depots_metadata follow by num of routes
num_vehicle_depots_metadata = sorted(num_vehicle_depots_metadata.items(), key=lambda x:x[1], reverse=True)

# Tính toán thêm chi phí luân chuyển xe giữa các depot
for i, num_vehicle_depot_metadata in enumerate(num_vehicle_depots_metadata[:-1]):
    num_vehicle_to_delivery = num_vehicle_depots_metadata[i+1][1] # Số lượng xe luân chuyển từ depot i sang depot i + 1
    for _ in range(num_vehicle_to_delivery):
        total_distance += D_pairwise[i][i+1] # khoảng cách từ depot i đến depot i + 1
        total_time_serving += caculate_time_travel(D_pairwise[i][i+1], v)

print("======== After clustering and routing for all depots and customers ========")
print("Total Demand: " + str(total_demand))
print("Total distance: " + str(total_distance) + " km")
print("Total time_serving: " + str(total_time_serving) + " minutes = " + str(total_time_serving / 60) + " hours")