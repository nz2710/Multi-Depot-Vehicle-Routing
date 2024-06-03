import pandas as pd
import numpy as np

# Đọc dữ liệu từ file, sử dụng khoảng trắng làm dấu phân cách và không có header
df = pd.read_csv('pr01.txt', sep='\s+', header=None)

# Xác định các cột tọa độ là cột 1 (longitude) và cột 2 (latitude), chỉ số cột bắt đầu từ 0
# Chuyển đổi cột longitude và latitude sang radian
df[1] = np.radians(df[1])
df[2] = np.radians(df[2])

# Lưu kết quả vào file mới
df.to_csv('modified_pr01.txt', index=False, header=None, sep=' ')
