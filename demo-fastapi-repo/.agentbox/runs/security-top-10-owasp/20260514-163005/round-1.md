**⚠ 11 lỗi trên 4 file — project đang EXPOSED tới SQL injection, SSRF, JWT bypass và secret leak**

### `vulnerable_demo.py` (6 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | CRITICAL | Command Injection | dòng 38 | `subprocess.check_output(..., shell=True)` với `host` từ user cho phép chèn `; cat /etc/passwd` để RCE. Đây là đường tấn công trực tiếp vào hệ thống. [A03] |
| 2 | HIGH | SQL Injection | dòng 28-29 | Query ghép chuỗi với `username` đi thẳng vào SQL; payload như `x' OR '1'='1` có thể làm lộ toàn bộ bảng users. [A03] |
| 3 | HIGH | XSS | dòng 67 | `account_id` được nhúng thẳng vào query, attacker có thể đổi ID để đọc bản ghi người khác; đây là IDOR/broken access control. [A01] |
| 4 | HIGH | SSRF | dòng 98 | `requests.get(url)` nhận URL từ user, nên attacker có thể ép server gọi `http://127.0.0.1` hoặc metadata service `169.254.169.254`. [A10] |
| 5 | HIGH | JWT bypass | dòng 107 | `jwt.decode(..., verify_signature=False)` bỏ qua xác thực chữ ký, nên token giả mạo có thể được chấp nhận. Ví dụ sửa payload `username=admin` là có thể impersonate. [A07] |
| 6 | MEDIUM | Secret leak | dòng 21-22 | `SECRET_KEY` và `API_TOKEN` hardcoded trong source; nếu repo hoặc image bị lộ, attacker có thể tái sử dụng secret thật. [A02] |

### `auth.py` (3 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | HIGH | SQL Injection | dòng 28-29 | `username` và `password` được nối trực tiếp vào query; payload như `' OR 1=1 --` có thể bypass login và đọc dữ liệu nhạy cảm. [A03] |
| 2 | HIGH | JWT bypass | dòng 42 | `jwt.decode(token, options={"verify_signature": False})` chấp nhận token không kiểm chữ ký, mở cửa cho giả mạo danh tính. [A07] |
| 3 | MEDIUM | Timing Attack | dòng 34-37 | So sánh token bằng `==` làm lộ khác biệt thời gian, attacker có thể dò dần giá trị bí mật qua side-channel. [A02] |

### `main.py` (1 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | MEDIUM | SSRF | dòng 43-44 | `requests.get("https://slow-api.com/data")` nằm trong `async def`, làm block event loop; đây là exposure về availability hơn là exploit trực tiếp. [A04] |

### `requirements.txt` (1 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | MEDIUM | Outdated Component | dòng 3 | `requests==2.20.0` là version cũ, tăng exposure tới CVE đã biết và làm giảm độ an toàn supply chain. [A06] |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | vulnerable_demo.py, auth.py, main.py, requirements.txt |
| Tổng finding | 11 |
| Mức độ cao nhất | CRITICAL |

### Kết luận

Đây là code demo cố ý chứa lỗi, nhưng nếu là code thật thì project đang exposed rất nặng và nên chặn release ngay. Điểm nguy hiểm nhất là command injection, SQL injection, và JWT bypass vì chúng có thể dẫn tới RCE hoặc chiếm quyền truy cập.
