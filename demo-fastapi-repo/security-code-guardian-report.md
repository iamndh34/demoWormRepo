**⚠ 9 lỗi trên 4 file — project đang exposed tới SQL injection, secret lộ và auth bypass**

### `auth.py` (3 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | CRITICAL | Hardcoded Secret | dòng 9 | `SECRET_KEY = "super-secret-key-12345"` là secret nhúng thẳng trong source. Nếu đây là key thật, attacker có thể giả mạo token hoặc ký dữ liệu trái phép. [A02] |
| 2 | HIGH | SQL Injection | dòng 16-18 | Query `f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"` nối trực tiếp input vào SQL. Payload kiểu `' OR '1'='1' --` có thể bypass đăng nhập và đọc dữ liệu người dùng. [A03] |
| 3 | HIGH | JWT bypass | dòng 28-29 | `jwt.decode(..., options={"verify_signature": False})` bỏ xác thực chữ ký, nên token giả có thể được chấp nhận như thật. Attacker chỉ cần sửa payload token và gửi lại. [A07] |

### `vulnerable_demo.py` (5 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | CRITICAL | Command Injection | dòng 27-28 | `subprocess.check_output(f"ping -c 1 {host}", shell=True)` cho phép chèn lệnh qua `host`. Ví dụ nhập `8.8.8.8; cat /etc/passwd` có thể dẫn tới RCE. [A03] |
| 2 | CRITICAL | SQL Injection | dòng 20-23 | `query = f"SELECT * FROM users WHERE username = '{username}'"` đưa thẳng input vào SQL. Payload như `x' UNION SELECT ...` có thể lộ toàn bộ bảng. [A03] |
| 3 | HIGH | XSS | dòng 34-35 | Trả về HTML với `f"<html><body><h1>Hello, {name}!</h1></body></html>"` mà không escape. Nếu `name = <script>alert(1)</script>` thì trình duyệt sẽ chạy script. [A03] |
| 4 | CRITICAL | Hardcoded Secret | dòng 40-41 | `SECRET_KEY = "supersecret123"` và `API_TOKEN = "AKIAIOSFODNN7EXAMPLE"` là bí mật nhúng cứng. Nếu đây là giá trị thật, attacker có thể dùng để mạo danh dịch vụ hoặc truy cập tài nguyên cloud. [A02] |
| 5 | HIGH | IDOR | dòng 48-51 | `SELECT * FROM accounts WHERE id = {account_id}` chỉ dựa vào ID do caller kiểm soát mà không thấy kiểm tra ownership. Đổi `account_id` sang ID người khác có thể đọc dữ liệu tài khoản trái phép. [A01] |

### `templates/index.html` (1 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | LOW | XSS | dòng 8 | `onclick="confirmDelete()"` tự nó chưa chắc là lỗi, nhưng file có dấu hiệu HTML được dựng thủ công và nội dung không được ràng buộc rõ ràng. Nếu giá trị động lọt vào template theo kiểu tương tự mà không escape thì có thể mở đường cho XSS. [A03] |

### `migrations/001_risky_change.sql` (2 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | HIGH | Destructive Migration | dòng 2 | `ALTER TABLE users DROP COLUMN email;` xóa cột dữ liệu trực tiếp. Nếu đây chạy trên production, có thể gây mất dữ liệu người dùng và làm hỏng luồng phụ thuộc vào email. |
| 2 | MEDIUM | Bulk Update | dòng 5 | `UPDATE orders SET status = 'processed' WHERE created_at < '2020-01-01';` là thay đổi hàng loạt không thấy batching hay guardrail. Nếu điều kiện sai, dữ liệu đơn hàng có thể bị cập nhật sai diện rộng. |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | auth.py, vulnerable_demo.py, templates/index.html, migrations/001_risky_change.sql |
| Tổng finding | 9 |
| Mức độ cao nhất | CRITICAL |

### Kết luận

Repo này đang exposed khá rõ tới các lỗi nặng: SQL injection, command injection, hardcoded secret và JWT bypass. Nếu đây là code thật chứ không phải demo intentional, mình khuyên chặn release ngay và xử lý các điểm CRITICAL/HIGH trước.