1. Phân cụm kmean với số cụm = số depot
2. Với mỗi depot, tạo các route thỏa mãn constranst số xe, time serving total, capacitied
3. Chọn serving depot có số route lớn nhất => nhỏ nhất
    Ví dụ:
    Depot 1: 4 route : => Chọn 4 xe
    Depot 2: 3 route : => Luân chuyển 3 xe từ Depot 1 sang Depot 2 (+3 chi phí khoảng cách, +3 chi phí thời gian)
    Depot 3: 1 route : => Luân chuyển 1 xe từ Depot 2 sang Depot 1 (+1 chi phí khoảng cách, +1 chi phí thời gian)