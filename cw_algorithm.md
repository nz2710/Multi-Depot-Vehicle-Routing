# Thuật toán Routing

# Clark and Wright Savings Algorithm

## Xét trên các cụm được phục vụ bởi depot D

Ở đây ta định nghĩa các nodes được coi như là các customers

Bước 1: Tính toán các đại lượng savings giữa 2 node i, j theo công thức:

    s(i, j) = d(D, i) + d(D, j) - d(i, j)
    
    Trong đó:
    
    d là hàm số khoảng cách eclid
    
    D đại diện cho node depot

Bước 2: Sắp xếp mảng savings theo thứ tự giảm dần

Bước 3: Duyệt lần lượt các phần tử trong mảng savings
    
    Đối với đại lượng s(i,j) đang được xem xét, thoả mãn các constrant định nghĩa ban đầu, Ta tiến hành xem xét 3 trường hợp
    
    TH1: Nếu cả i và j chưa được gán cho một route => tạo một route mới bao gồm i và j 
    
    * Lưu ý: 1 router mới tương ứng với 1 vehicle mới <=> 1 unique customer chỉ được phục vụ bởi 1 unique vehicle *
    
    TH2: Nếu một trong hai node i hoặc j đã được assign một route r hiện có và điểm i hoặc j đó không nằm bên trong route r
        
        Điểm nằm bên trong: là điểm không liền kề với depot D
        
        => Liên kết (i, j) được thêm vào route r
    
    TH3: Cả 2 node i và j đều đã được gán cho hai route r và R hiện có và cả i và j đều không nằm trong r và R
        
        => hợp nhất 2 route r và R

Bước 4: Nếu mảng savings chưa được duyệt hết, tiếp tục quay lại bước 3
        
        Nếu mảng savings đã được duyệt hết => Kết thúc thuật toán