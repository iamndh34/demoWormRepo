# security-code-guardian — saved by agentbox --save

Generated: 2026-05-11T04:33:39Z

**⚠ 12 lỗi trên 4 file — project đang EXPOSED tới SQL injection, command injection, SSRF, XSS và bypass xác thực**

### `vulnerable_demo.py` (8 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | CRITICAL | Command Injection | dòng 31-32 | `subprocess.check_output(f"ping -c 1 {host}", shell=True)` cho attacker điều khiển lệnh qua `host`. Payload kiểu `8.8.8.8; cat /etc/passwd` có thể dẫn tới RCE. [A03] |
| 2 | CRITICAL | Insecure Deserialization | dòng 77 | `pickle.loads(body)` nạp dữ liệu do user gửi trực tiếp vào deserializer nguy hiểm. Payload pickle crafted có thể kích hoạt gadget chain và chạy code tùy ý. [A08] |
| 3 | CRITICAL | XSS | dòng 24-25 | `f"<html><body><h1>Hello, {name}!</h1></body></html>"` render `name` vào HTML không escape. Payload như `<img src=x onerror=alert(1)>` sẽ chạy script trong trình duyệt nạn nhân. [A03] |
| 4 | CRITICAL | SQL Injection | dòng 16-19 | `query = f"SELECT * FROM users WHERE username = '{username}'"` ghép trực tiếp input vào SQL. Payload như `' OR '1'='1` có thể bypass đăng nhập và dump dữ liệu. [A03] |
| 5 | CRITICAL | SSRF | dòng 98 | `requests.get(url)` lấy đích từ `url` do user kiểm soát. Attacker có thể trỏ sang `http://169.254.169.254/latest/meta-data/` hoặc localhost để đọc tài nguyên nội bộ. [A10] |
| 6 | HIGH | Weak Hash | dòng 53-57 | `hashlib.md5(password.encode()).hexdigest()` dùng MD5 cho mật khẩu là yếu và dễ brute-force/rainbow table. Nếu hash bị lộ, mật khẩu người dùng bị crack nhanh hơn nhiều. [A02] |
| 7 | HIGH | Hardcoded Secret | dòng 53-54 | `SECRET_KEY = "supersecret123"` và `API_TOKEN = "AKIAIOSFODNN7EXAMPLE"` là secret hardcoded. Nếu đây là giá trị thật, attacker có thể dùng để ký token hoặc truy cập dịch vụ liên quan. [A02] |
| 8 | HIGH | JWT bypass | dòng 107 | `jwt.decode(token, options={"verify_signature": False})` bỏ kiểm tra chữ ký, nên token giả mạo vẫn được chấp nhận. Payload tự ký với `username=admin` có thể bypass auth hoàn toàn. [A07] |

### `auth.py` (3 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | CRITICAL | Hardcoded Secret | dòng 8 | `SECRET_KEY = "super-secret-key-12345"` lộ secret ngay trong source. Nếu key này dùng cho JWT hoặc session signing, attacker có thể forge token hợp lệ. [A02] |
| 2 | CRITICAL | SQL Injection | dòng 15-17 | Query `f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"` cho phép chèn payload như `username = "' OR 1=1 --"` để bypass xác thực. [A03] |
| 3 | HIGH | JWT bypass | dòng 23-24 | `jwt.decode(token, options={"verify_signature": False})` chấp nhận payload không có chữ ký hợp lệ. Token giả mạo có thể được dùng để impersonate user. [A07] |

### `main.py` (2 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | HIGH | SQL Injection | dòng 26-27 | `cursor.execute(f"SELECT * FROM profiles WHERE user_id = {u_id}")` vẫn là query ghép chuỗi từ dữ liệu lấy ra. Nếu nguồn `u_id` bị thao túng, attacker có thể sửa logic truy vấn và đọc dữ liệu ngoài phạm vi dự kiến. [A03] |
| 2 | MEDIUM | SSRF/Blocking IO | dòng 33-34 | `requests.get("https://slow-api.com/data")` trong `async def` không phải SSRF vì URL đã cố định, nhưng nó chặn event loop và có thể làm giảm khả dụng của API. Nếu endpoint này sau này nhận URL từ user thì sẽ chuyển thành SSRF. [A10] |

### `migrations/001_risky_change.sql` (1 lỗi)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | MEDIUM | Dangerous Migration | dòng 2-5 | `ALTER TABLE users DROP COLUMN email;` và `UPDATE orders ...` là thay đổi schema/data có thể phá dữ liệu hoặc gây downtime nếu chạy nhầm môi trường. Payload ở đây không phải attacker input, nhưng migration này có blast radius vận hành đáng kể. |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | vulnerable_demo.py, auth.py, main.py, migrations/001_risky_change.sql |
| Tổng finding | 12 |
| Mức độ cao nhất | CRITICAL |

### Kết luận

Project này đang exposed khá nặng ở các điểm injection, secret hardcoding và bypass xác thực; nếu đây là code thật thì mình khuyên chặn release ngay. Phần `migrations/001_risky_change.sql` thiên về rủi ro vận hành hơn là security thuần, nhưng tổng thể vẫn không an toàn để deploy.
