1. Phân cụm kmean các nodes với số cụm = số depot
2. Gán các depot tương ứng với các centroid gần nhất
2. Với mỗi depot, tạo các route theo thuật toán Clark and Wright Savings thỏa mãn constranst time serving total, capacitied => xem cw_algorithm.md
3. Thuật toán phân bố xe (nếu số lượng xe có sẵn không đáp ứng đủ)
   - Sau khi routing xong, sắp xếp các depot theo thứ tự số lượng routes trong mỗi depot từ lớn nhất đến nhỏ nhất
   - Giả sử số lượng xe ban đầu là m, số lượng depot là d => số lượng xe được chia đều cho mỗi depot: m / d
   - Sau khi chia đều, nếu vẫn còn thừa xe, thì tiếp tục chia cho các depot còn nhu cầu theo thứ tự đã sắp xếp (lớn nhất đến nhỏ nhất)
4. Thuật toán luân chuyển xe
   - Sắp xếp thứ tự ưu tiên các depot (tính distance đến depot gần nhất) từ nhỏ nhất đến lớn nhất
   - Với depot d, với các xe hiện tại, tiến hành routing cho các routes có total_time_serving được sắp xếp từ lớn nhất đến nhỏ nhất
   - Nếu trong depot d vẫn còn các routes chưa được serving (thời gian serving của các xe trong depot d đã hết hoặc không đủ để đi route tiếp theo)
   => Luân chuyển các xe từ depot gần nhất d (dc) sang routing cho các route chưa được serving, xuất phát từ dc