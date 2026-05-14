# security-code-guardian — saved by agentbox --save

Generated: 2026-05-11T04:37:27Z

**⚠ 14 lỗi trên 5 file — project đang EXPOSED tới SQL injection, command injection, SSRF, JWT bypass và lộ secret**

### `vulnerable_demo.py` (6 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | CRITICAL | Command Injection | dòng 28-29 | `subprocess.check_output(f"ping -c 1 {host}", shell=True)` đưa `host` từ user vào shell. Payload như `8.8.8.8; cat /etc/passwd` có thể chạy lệnh tùy ý trên server. [A03] |
| 2 | CRITICAL | SQL Injection | dòng 24-25 | Query `f"SELECT * FROM users WHERE username = '{username}'"` nối thẳng input vào SQL. Ví dụ `username = "' OR '1'='1' --"` có thể làm điều kiện luôn đúng và lộ dữ liệu. [A03] |
| 3 | CRITICAL | Insecure Deserialization | dòng 59-61 | `pickle.loads(body)` nhận dữ liệu từ request body rồi giải tuần tự hóa trực tiếp. Payload pickle độc hại có thể kích hoạt object/gadget chain dẫn tới RCE. [A08] |
| 4 | CRITICAL | SSRF | dòng 82-83 | `requests.get(url)` cho phép user điều khiển đích request. Attacker có thể trỏ vào `http://localhost` hoặc metadata service để quét mạng nội bộ/lộ credential. [A10] |
| 5 | HIGH | XSS | dòng 35-37 | Trả HTML bằng `f"<html><body><h1>Hello, {name}!</h1></body></html>"` mà không escape. Nếu `name = <script>alert(1)</script>` thì browser sẽ chạy script trong session nạn nhân. [A03] |
| 6 | HIGH | JWT bypass | dòng 89-91 | `jwt.decode(token, options={"verify_signature": False})` tắt kiểm tra chữ ký. Attacker chỉ cần sửa payload token rồi gửi lại là có thể giả mạo danh tính. [A07] |

### `auth.py` (3 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | CRITICAL | Hardcoded Secret | dòng 16 | `SECRET_KEY = "super-secret-key-12345"` là secret nhúng thẳng trong source. Nếu đây là key thật, attacker có thể giả mạo token hoặc ký dữ liệu trái phép. [A02] |
| 2 | HIGH | SQL Injection | dòng 24-26 | `f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"` cho phép chèn SQL qua cả username lẫn password. Payload kiểu `' OR 1=1 --` có thể bypass đăng nhập và đọc dữ liệu. [A03] |
| 3 | HIGH | JWT bypass | dòng 37-38 | `jwt.decode(token, options={"verify_signature": False})` bỏ xác thực chữ ký, nên token giả có thể được chấp nhận như thật. Attacker chỉ cần chỉnh payload rồi gửi lại. [A07] |

### `main.py` (3 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | HIGH | N+1 Query | dòng 26-31 | Vòng lặp `for` gọi `cursor.execute(f"SELECT * FROM profiles WHERE user_id = {u_id}")` cho từng user. Điều này mở rộng bề mặt lạm dụng hiệu năng và có thể tạo áp lực DB lớn khi danh sách user tăng. |
| 2 | MEDIUM | SQL Injection | dòng 29 | `f"SELECT * FROM profiles WHERE user_id = {u_id}"` nối trực tiếp biến vào query. Nếu luồng dữ liệu thay đổi sang input không tin cậy, attacker có thể chèn biểu thức SQL. [A03] |
| 3 | MEDIUM | Blocking I/O | dòng 35-37 | `requests.get(...)` được gọi trong `async def`, làm treo event loop khi remote chậm. Đây không phải lỗ hổng bảo mật trực tiếp, nhưng có thể bị lạm dụng để làm giảm khả dụng. |

### `migrations/001_risky_change.sql` (2 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | HIGH | Destructive Migration | dòng 2 | `ALTER TABLE users DROP COLUMN email;` xóa cột dữ liệu trực tiếp. Nếu chạy trên production, có thể gây mất dữ liệu và làm hỏng luồng phụ thuộc vào email. |
| 2 | MEDIUM | Bulk Update | dòng 5 | `UPDATE orders SET status = 'processed' WHERE created_at < '2020-01-01';` là thay đổi hàng loạt không thấy guardrail hay batching. Nếu điều kiện sai, dữ liệu đơn hàng có thể bị cập nhật rộng ngoài ý muốn. |

### `requirements.txt` (0 lỗi được xác nhận, nhưng có rủi ro)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | MEDIUM | Outdated Dependency | dòng 3 | `requests==2.20.0` là bản rất cũ; nếu đây là dependency thật thì nên kiểm tra CVE/bugfix vì project có thể đang exposed tới rủi ro supply-chain hoặc bug đã biết. |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | vulnerable_demo.py, auth.py, main.py, migrations/001_risky_change.sql, requirements.txt |
| Tổng finding | 14 |
| Mức độ cao nhất | CRITICAL |

### Kết luận

Repo này đang exposed khá nặng: có command injection, SQL injection, SSRF, JWT bypass và hardcoded secret. Nếu đây là code thật chứ không phải demo intentional, theo mình nên chặn release ngay và xử lý các điểm CRITICAL/HIGH trước.
