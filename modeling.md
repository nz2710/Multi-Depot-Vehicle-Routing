# Mô hình hoá bài toán 

## Các biến

N = {0, 1, 2, ..., n}: Đại diện cho tập hợp customers 1-n phục vụ bởi depot 0

N' = N \ {0}: Đại diện cho tập hợp customers 1-n

K = {1, 2, 3, ..., k}: Đại diện cho tập hợp các xe 1-k

Q: Đại diện cho sức chứa (capacity) tối đa (limit) của mỗi xe

d(i): Đại diện cho nhu cầu (demand) của customer i

t(ij): Đại diện cho travel time của vehicle giữa customer i và customer j

c(ij): Đại diện cho travel cost (distance) của vehicle giữa customer i và customer j

x(ij): Biến quyết định. Nếu serving từ i đến j thì x(ij) = 1 và ngược lại = 0

y(ik): Biến quyết định. Nếu customer i được phục vụ (served) bởi vehicle k, y(ik) = 1 và ngược lại = 0

## Các điều kiện ràng buộc

min f = Sum(i thuộc N)Sum(j thuộc N)[c(ij)x(ij)] (1) => minimize hàm số travel cost (distance) của tất cả vehicle

sum(k thuộc K)[y(ik)]== 1, với mọi i thuộc N' => một customer chỉ được phục vụ duy nhất bởi một vehicle

sum(j thuộc N)[x(ij)] = sum(m thuộc N)[x(mi)], với mọi i thuộc N

x(ij)y(ik) = x(ji)y(jk), với mọi i,j thuộc N', mọi k thuộc K => chỉ ra rằng nếu customer i và customer j đang trên đường đi của phương tiện, phương tiện sẽ cung cấp dịch vụ cho cả customer 1 và 2

sum(i thuộc N)[d(i)y(ik)] <= Q => Tổng nhu cầu của customers cho bất kỳ vehicle nào không vượt quá Q

Đặt Zk = Sum(i thuộc N)Sum(j thuộc N)[c(ij)x(ij)y(ik)y(jk)]
Sum(k thuộc K)Zk <= Z * max duration route: Thời gian serving trong 1 route không vượt quá max duration route, trong đó Z là số lần Zk = 0 với k thuộc K