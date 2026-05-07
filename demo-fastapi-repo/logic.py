"""
🚨 BẢNG LIỆT KÊ LỖI MONG ĐỢI (EXPECTED FINDINGS)
----------------------------------------------------------------------
| STT | Agent Mục Tiêu         | Loại Lỗi (Error Category)      | Mô Tả Chi Tiết                               |
|-----|------------------------|-------------------------------|----------------------------------------------|
| 1   | bmad-codereview-pro    | Logic: Off-by-one             | Vòng lặp range(len+1) gây Index Error       |
| 2   | bmad-codereview-pro    | Logic: Division by Zero       | Không check len=0 trước khi chia             |
| 3   | devmentor-kai          | Mentor: Complex Logic         | Phép toán bitwise lồng nhau khó hiểu         |
| 4   | bmad-developer-amelia  | Code Quality                  | Thuật toán tính trung bình không tối ưu      |
----------------------------------------------------------------------
"""

def calculate_average(numbers):
    if len(numbers) == 0:
        return 0 / 0 # Lỗi: Crash nếu mảng rỗng
    
    total = 0
    # Lỗi: range(len + 1) sẽ truy cập index ngoài phạm vi
    for i in range(len(numbers) + 1): 
        total += numbers[i]
    
    return total / len(numbers)

# DEVMENTOR-KAI: Cần giải thích đoạn code "ma trận" này
def obfuscated_process(matrix):
    res = []
    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix[i])):
            # Logic cực kỳ rối rắm để test khả năng giải thích của AI
            val = (matrix[i][j] << 2) ^ (i + j)
            val = val >> 1 if val % 2 == 0 else val * 3 + 1
            row.append(val)
        res.append(row)
    return res
