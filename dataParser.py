import glob

def prParser(pr_path):
    with open(pr_path, "r", encoding="utf8") as fr:
        lines = fr.readlines()
        lines = [line.replace("\n", "") for line in lines]
        type, m, n, t = int(lines[0].split()[0]), int(lines[0].split()[1]), int(lines[0].split()[2]), int(lines[0].split()[3])
        depots_info = lines[-t:]
        customers_info = lines[t+1:-t]
        return customers_info, depots_info, m, n, t

pr_list_paths = glob.glob("data/C-mdvrptw/*")

customers_info, depots_info, m, n, t = prParser("data/C-mdvrptw/pr24b")

print("data/C-mdvrptw/pr24b")