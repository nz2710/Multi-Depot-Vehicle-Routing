import numpy as np
import config
from utils import *
from constraint import *
from cw import *
import pandas as pd
import random
from tqdm import tqdm
import glob

def prParser(pr_path):
    with open(pr_path, "r", encoding="utf8") as fr:
        lines = fr.readlines()
        lines = [line.replace("\n", "") for line in lines]
        _, num_vehicles, _, num_depots = int(lines[0].split()[0]), int(lines[0].split()[1]), int(lines[0].split()[2]), int(lines[0].split()[3])
        max_duration_route = int(lines[1].split()[0])
        vehicle_capacity = int(lines[1].split()[1])
        depots_info = lines[-num_depots:]
        customers_info = lines[num_depots+1:-num_depots]
        return customers_info, depots_info, num_vehicles, num_depots, max_duration_route, vehicle_capacity

pr_list_paths = glob.glob("data/C-mdvrptw/*")

customers_info, depots_info, num_vehicles, num_depots, max_duration_route, vehicle_capacity = prParser("data/C-mdvrptw/pr20")

NUM_TAKE = 10000

df = pd.read_csv("data/All_Places_of_Worship.csv")

countrys = df["COUNTY"].values.tolist()

countrys = list(set(countrys))

print(countrys)

X_coor = df["X"].values.tolist()
Y_coor = df["Y"].values.tolist()

min_x_coor = min(X_coor)
max_x_coor = max(X_coor)

min_y_coor = min(Y_coor)
max_y_coor = max(Y_coor)

print("Min X coor: " + str(min_x_coor))
print("Max X coor: " + str(max_x_coor))

print("Min Y coor: " + str(min_y_coor))
print("Max Y coor: " + str(max_y_coor))

coors = []

for index, x_coor in enumerate(X_coor):
    coors.append([X_coor[index], Y_coor[index]])

# random.shuffle(coors)
coors = coors[0: NUM_TAKE]

infor_column = "NAME"

infor_data = df[infor_column].values.tolist()[0: NUM_TAKE]

info_mapping = {}

for index, _ in enumerate(infor_data):
    info_mapping[index] = infor_data[index]

# np.random.seed(config.SEED_NUMBER)

# Time đơn vị tính theo phút
# Distance đơn vị tính theo km
# Vận tốc v tính theo km/h

X_for_kmean, De_for_kmean, X_pairwise, D_pairwise, T_pairwise = caculate_pairwise(customers_info, depots_info, v=config.V)

# sort by demand
X_pairwise = sorted(X_pairwise[num_depots:], key=lambda x:x[2], reverse=True)

MAX_DEMAND = X_pairwise[0][2]
MIN_DEMAND = X_pairwise[-1][2]

print("Max demand: " + str(X_pairwise[0][2]))
print("Min demand: " + str(X_pairwise[-1][2]))

# sort by duration
X_pairwise = sorted(X_pairwise, key=lambda x:x[3], reverse=True)

print("Max duration: " + str(X_pairwise[0][3]))
print("Min duration: " + str(X_pairwise[-1][3]))

MAX_DURATION = X_pairwise[0][3]
MIN_DURATION = X_pairwise[-1][3]

# random demand, duration, depot info

num_vehicles = int(len(infor_data) / 120)
max_duration_route = 800
max_demand = 200
num_depots = int(len(infor_data) / 80)

DATA = []

first_line = "6 " + str(num_vehicles) + " " + str(len(infor_data)) + " " + str(num_depots)

DATA.append(first_line)

for _ in range(num_depots):
    DATA.append(str(max_duration_route) + " " + str(max_demand))

last_index = 0

coors_save = [[0, 0]]

for index, _ in enumerate(tqdm(coors)):
    x_coor = 0
    y_coor = 0
    while [x_coor, y_coor] in coors_save:
        x_coor = random.uniform(min_x_coor, max_x_coor)
        y_coor = random.uniform(min_y_coor, max_y_coor)
    item = str(index + 1) + " " + str(x_coor) + " " + str(y_coor) + " " + str(random.randint(MIN_DEMAND, MAX_DEMAND)) + " " + str(random.randint(MIN_DURATION, MAX_DURATION))
    DATA.append(item)
    last_index = index
    coors_save.append([x_coor, y_coor])

last_index = last_index + 1

for index in range(num_depots):
    x_coor = coors_save[index][0]
    y_coor = coors_save[index][1]
    while [x_coor, y_coor] in coors_save:
        x_coor = random.uniform(min_x_coor, max_x_coor)
        y_coor = random.uniform(min_y_coor, max_y_coor)
    item = str(last_index + index + 1) + " " + str(x_coor) + " " + str(y_coor) + " 0 " + " 0 "
    DATA.append(item)
    coors_save.append([x_coor, y_coor])

with open("data/C-mdvrptw/pr25", "w", encoding="utf8") as fw:
    for item in tqdm(DATA):
        fw.write(item + "\n")