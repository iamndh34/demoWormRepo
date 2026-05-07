"""
🚨 BẢNG LIỆT KÊ LỖI MONG ĐỢI (EXPECTED FINDINGS)
----------------------------------------------------------------------
| STT | Agent Mục Tiêu  | Loại Lỗi (Error Category)      | Mô Tả Chi Tiết                               |
|-----|-----------------|-------------------------------|----------------------------------------------|
| 1   | error-auditor   | Error: Bare Except            | Except không có kiểu dữ liệu (nuốt lỗi)      |
| 2   | error-auditor   | Error: Missing Logging        | Dùng print thay vì thư viện logging chuẩn    |
| 3   | error-auditor   | Error: Silent Failure         | Pass trong block except mà không làm gì      |
----------------------------------------------------------------------
"""

def process_file(path):
    try:
        f = open(path, 'r')
        data = f.read()
        print(f"Read data: {data}")
    except:
        # Lỗi: Cực kỳ nguy hiểm, nuốt cả KeyboardInterrupt/SystemExit
        pass 

def api_call():
    result = {"status": "fail"}
    # Lỗi: Không log lại lỗi, developer không biết tại sao fail
    print("API Call failed") 
    return result
