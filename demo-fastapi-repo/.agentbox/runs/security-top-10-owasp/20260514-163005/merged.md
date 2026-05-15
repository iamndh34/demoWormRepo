**⚠ 15 lỗi trên 5 file — project đang EXPOSED tới SQL injection, JWT bypass, SSRF, command injection và secret leak**

### `auth.py` (3 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | HIGH | SQL Injection | dòng 28-29 | Query ghép chuỗi trực tiếp từ `username` và `password` vào SQL. Attacker có thể dùng payload như `' OR '1'='1` để bypass đăng nhập và đọc dữ liệu users. [A03] |
| 2 | HIGH | Hardcoded Secret | dòng 20 | `SECRET_KEY` nằm thẳng trong source code, nên nếu repo hoặc image bị lộ thì attacker có thể dùng key này để giả mạo token hoặc giải mã dữ liệu liên quan. [A02] |
| 3 | HIGH | JWT Bypass | dòng 42 | `jwt.decode(..., verify_signature=False)` chấp nhận token không kiểm chữ ký. Attacker chỉ cần sửa payload, ví dụ đổi `username` thành `admin`, là có thể giả mạo danh tính. [A07] |

### `vulnerable_demo.py` (8 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | HIGH | Command Injection | dòng 38 | `subprocess.check_output(..., shell=True)` với `host` từ user cho phép chèn `; cat /etc/passwd` hoặc `&& id` để chạy lệnh tùy ý. [A03] |
| 2 | HIGH | SQL Injection | dòng 67 | `account_id` được nhúng trực tiếp vào query. Attacker có thể đổi tham số thành `1 OR 1=1` để đọc bản ghi ngoài quyền. [A03] |
| 3 | HIGH | Insecure Deserialization | dòng 77 | `pickle.loads(body)` xử lý dữ liệu do user kiểm soát; payload pickle độc hại có thể kích hoạt thực thi code khi deserialize. [A08] |
| 4 | HIGH | Unsafe YAML Load | dòng 89 | `yaml.load(..., Loader=yaml.Loader)` cho phép object construction nguy hiểm từ input. Payload YAML crafted có thể dẫn tới RCE hoặc đọc object ngoài ý muốn. [A05] |
| 5 | HIGH | SSRF | dòng 98 | `requests.get(url)` fetch URL do user cung cấp, nên attacker có thể trỏ tới `http://127.0.0.1:...` hoặc metadata service để pivot vào mạng nội bộ. [A10] |
| 6 | HIGH | JWT Bypass | dòng 107 | `jwt.decode(..., verify_signature=False)` bỏ qua xác thực chữ ký. Attacker có thể tự ký giả hoặc sửa payload để mạo danh user. [A07] |
| 7 | HIGH | Secret Exposure | dòng 53 | `SECRET_KEY` hardcoded trong code, làm lộ material nhạy cảm nếu source/build artifact bị truy cập. [A02] |
| 8 | HIGH | Secret Logging | dòng 118 | Log ghi thẳng `password` từ request. Nếu log bị đọc được, attacker sẽ thu được credential thật; ví dụ đăng nhập admin sẽ bị lộ ngay trong log. [A09] |

### `main.py` (2 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | MEDIUM | N+1 Query | dòng 30-36 | Vòng lặp gọi `cursor.execute(...)` cho từng `u_id`, tạo mẫu N+1. Đây là exposure về hiệu năng và có thể bị lạm dụng để làm chậm hệ thống khi số bản ghi tăng. |
| 2 | MEDIUM | Blocking IO | dòng 43-44 | `requests.get(...)` chạy đồng bộ bên trong `async def`, làm nghẽn event loop FastAPI. Attacker có thể giữ kết nối chậm để làm giảm throughput của service. |

### `requirements.txt` (1 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | MEDIUM | Outdated Dependency | dòng 1-5 | `requests==2.20.0` và các pin cũ cho thấy dependency đã lỗi thời. Nếu version này có CVE reachable trong runtime, project sẽ bị expose tới supply-chain risk. [A06] |

### `migrations/001_risky_change.sql` (1 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | MEDIUM | Dangerous Migration | dòng 2-5 | `ALTER TABLE users DROP COLUMN email;` và update hàng loạt không có kiểm soát rollback/batching. Nếu chạy trên production, thay đổi này có thể gây mất dữ liệu hoặc downtime. [A04] |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | auth.py, vulnerable_demo.py, main.py, requirements.txt, migrations/001_risky_change.sql |
| Tổng finding | 15 |
| Mức độ cao nhất | HIGH |