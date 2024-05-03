# Solving the capacitated vehicle routing problem with time windows 

## Các biến

N = {0, 1, 2, ..., n}: Đại diện cho tập hợp customers 1-n phục vụ bởi depot 0

N' = N \ {0}: Đại diện cho tập hợp customers 1-n

K = {1, 2, 3, ..., k}: Đại diện cho tập hợp các xe 1-k

Q: Đại diện cho sức chứa (capacity) tối đa (limit) của mỗi xe

d(i): Đại diện cho nhu cầu (demand) của customer i

s(i): Thời gian phục vụ (service duration hay service time lasted) cho customer i

e(i): beginning of time window (earliest time for start of service), if any

l(i): end of time window (latest time for start of service), if any

c(ij): Đại diện cho travel cost của vehicle giữa node i và node j

t(ij): Đại diện cho travel time của vehicle giữa node i và node j

b(i) là thời điểm service start tại node i

x(ij): Biến quyết định. Nếu edge(i, j) is used, it is 1; otherwise, it is 0

y(ik): Biến quyết định. Nếu customer i được phục vụ (served) bởi vehicle k, it is 1; otherwise, it is 0

## Các điều kiện ràng buộc

min f = Sum(i thuộc N)Sum(j thuộc N)[c(ij)x(ij)] (1) => minimize hàm số travel cost của tất cả vehicle

sum(k thuộc K)[y(ik)]== 1, với mọi i thuộc N' => một customer chỉ được phục vụ duy nhất bởi một vehicle

sum(j thuộc N)[x(ij)] = sum(m thuộc N)[x(mi)], với mọi i thuộc N => show that the departure edge of node i is equal to the arrival edge of node i

x(ij)y(ik) = x(ji)y(jk), với mọi i,j thuộc N', mọi k thuộc K => chỉ ra rằng nếu customer i và customer j đang trên đường đi của phương tiện, phương tiện sẽ cung cấp dịch vụ cho cả customer 1 và 2

sum(i thuộc N)[d(i)y(ik)] <= Q => Tổng nhu cầu của customers cho bất kỳ vehicle nào không vượt quá Q

b(j) >= b(i) + c(ij)x(ij) - M(1 - x(ij)), với mọi i,j thuộc N'; M (số đủ lớn - M có thể = max(i, j)[l(i) + c(ij) - e(j)])

e(i) <= b(i) <= l(i), với mọi i thuộc N'