import numpy as np
from scipy.spatial.distance import cdist
from dataParser import customers_info, depots_info, m, n, t
import math

np.random.seed(11) # làm điều này để việc khởi tạo các biến ngẫu nhiên ở 2 lần chạy khác nhau là giống nhau => xem hàm kmeans_init_centroids

def distance(node1, node2):
    square = math.pow((node1[0] - node2[0]), 2) + math.pow((node1[1] - node2[1]), 2)
    return math.sqrt(square)

class KmeanCore:

    def __init__(self) -> None:
        pass

    def kmeans_init_centroids(self, X, k):
        # Chọn ngẫu nhiên k điểm dữ liệu làm các centroid
        return X[np.random.choice(X.shape[0], k, replace=False)]

    def kmeans_assign_labels(self, X, centroids):
        # tính toán khoảng cách eclid giữa các điểm dữ liệu với các centroid
        D = cdist(X, centroids)
        # tập hợp các điểm gần nhất tương ứng với từng centroid
        return np.argmin(D, axis = 1)

    def kmeans_update_centroids(self, X, labels, K):
        centroids = np.zeros((K, X.shape[1]))
        for k in range(K):
            # Lẩy ra các điểm thuộc cluster k 
            Xk = X[labels == k, :]
            # Tính toán lại centroid của cluster k bằng cách lấy trung bình toạ độ
            centroids[k,:] = np.mean(Xk, axis = 0)
        return centroids

    def has_converged(self, centroids, new_centroids):
        # return True nếu tập hợp các centroids vòng lặp trước (centroids) và vòng lặp hiện tại (new_centroids) là như nhau
        return (set([tuple(a) for a in centroids]) == set([tuple(a) for a in new_centroids]))

    def kmeans(self, X, K):
        centroids = [self.kmeans_init_centroids(X, K)]
        labels = []
        it = 0 
        while True:
            labels.append(self.kmeans_assign_labels(X, centroids[-1]))
            new_centroids = self.kmeans_update_centroids(X, labels[-1], K)
            if self.has_converged(centroids[-1], new_centroids):
                break
            centroids.append(new_centroids)
            it += 1
        return (centroids[-1], labels[-1], it)

class KmeanMVRP:

    def __init__(self) -> None:
        self.kmean_core = KmeanCore()

    def kmean_assign_depots_closest_centroids(self, customers_info, depots_info, num_depots, num_clusters):
        # Tạo mảng dữ liệu customers, mỗi một hàng là cặp toạ độ (x, y) tương ứng với từng customer
        # X[0] => customer 0
        X = []
        for customer_info in customers_info:
            customer_info = " ".join(customer_info.split())
            x = float(customer_info.split()[1])
            y = float(customer_info.split()[2])
            X.append([x, y])
        X = np.array(X)
        # Tạo mảng dữ liệu depots
        De = []
        for depot_info in depots_info:
            depot_info = " ".join(depot_info.split())
            x = float(depot_info.split()[1])
            y = float(depot_info.split()[2])
            De.append([x, y])
        De = np.array(De)
        # Phân cụm các customers
        (centroids, labels, it) = self.kmean_core.kmeans(X, num_clusters)
        # Tạo centroids metadata, mỗi một key là tên kèm chỉ số centroid, value của key là một mảng bao gồm các customers thuộc cụm centroid
        centroids_metadata = {}
        for label in labels:
            centroids_metadata["centroid_" + str(label)] = []
        for label in labels:
            for i, label_ in enumerate(labels):
                if label_ == label:
                    centroids_metadata["centroid_" + str(label)].append(i)
            centroids_metadata["centroid_" + str(label)] = list(set(centroids_metadata["centroid_" + str(label)]))
        centroids_metadataKeys = list(centroids_metadata.keys())
        centroids_metadataKeys = sorted(centroids_metadataKeys, key=lambda kv: int(kv.split("_")[-1]))
        centroids_metadata_sorted = {i: centroids_metadata[i] for i in centroids_metadataKeys}
        # Gán các cụm customers với các depots sử dụng khoảng cách eclid giữa depot với centroid
        # DDC => Distance of depots with centroids
        ddc = cdist(De, centroids)
        # Get depot index for centroid
        difc = np.argmin(ddc, axis = 1)
        # Tạo depots metadata, mỗi một key là tên kèm chỉ số depot, value của key là một mảng bao gồm các centroids mà depot được assign
        depots_centroids_metadata = {}
        depots_customers_metadata = {}
        centroid_choosed_index = [-1]
        for depot_index in range(num_depots):
            list_centroids_for_depot = []
            min_distance_eclid = 9999999999
            for index_centroid, centroid in enumerate(centroids):
                if index_centroid not in centroid_choosed_index:
                    min_distance_eclid = min(min_distance_eclid, distance(De[depot_index], centroid))
            for index_centroid, centroid in enumerate(centroids):
                if min_distance_eclid == distance(De[depot_index], centroid) and index_centroid not in centroid_choosed_index:
                    list_centroids_for_depot.append(index_centroid)
                    centroid_choosed_index.append(index_centroid)
            list_centroids_for_depot = list(set(list_centroids_for_depot))
            depots_centroids_metadata["depot_" + str(depot_index)] = list_centroids_for_depot
            for i, centroid_depot in enumerate(list_centroids_for_depot):
                depots_customers_metadata[depot_index] = []
            for i, centroid_depot in enumerate(list_centroids_for_depot):
                depots_customers_metadata[depot_index].append(centroids_metadata_sorted["centroid_" + str(centroid_depot)])
        return centroids_metadata_sorted, depots_centroids_metadata, depots_customers_metadata
    
if __name__ == "__main__":
    app = KmeanMVRP()
    centroids_metadata_sorted, depots_centroids_metadata, depots_customers_metadata = app.kmean_assign_depots_closest_centroids(customers_info=customers_info, depots_info=depots_info, num_depots=t, num_clusters=8)
    print("="*100)
    print("Centroid customer metadata")
    print(centroids_metadata_sorted)
    print("="*100)
    print("Deport customer metadata")
    print(depots_customers_metadata)




