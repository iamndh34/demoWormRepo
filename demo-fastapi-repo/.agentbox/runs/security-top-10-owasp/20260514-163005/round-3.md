**⚠ 13 lỗi trên 4 file — project đang exposed tới SQL injection, JWT bypass, SSRF và lộ secret**

### `auth.py` (3 findings)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | CRITICAL | SQL Injection | dòng 28-29 | Query ghép trực tiếp `username` và `password` vào SQL. Attacker có thể dùng payload như `' OR '1'='1` để bypass đăng nhập và đọc/sửa dữ liệu. [A03] |
| 2 | CRITICAL | Hardcoded Secret | dòng 20 | `SECRET_KEY` nằm thẳng trong source code, nên nếu repo/log/build artifact lộ ra thì attacker có thể dùng secret này để giả mạo token hoặc truy cập trái phép. [A02] |
| 3 | HIGH | JWT Bypass | dòng 41-42 | `jwt.decode(..., options={"verify_signature": False})` chấp nhận token không kiểm chữ ký. Attacker có thể sửa payload rồi tự ký giả hoặc dùng token forged để impersonate user. [A07][A02] |

### `vulnerable_demo.py` (7 findings)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | CRITICAL | Command Injection | dòng 38 | `subprocess.check_output(..., shell=True)` với `host` từ user cho phép chèn payload như `8.8.8.8; cat /etc/passwd` để RCE. [A03] |
| 2 | CRITICAL | SQL Injection | dòng 28-29 | Query SQL ghép chuỗi với `username`; payload như `' UNION SELECT ...` có thể đọc dữ liệu nhạy cảm hoặc bypass auth. [A03] |
| 3 | CRITICAL | XSS | dòng 18-19 | `name` được nhúng thẳng vào HTML response. Payload như `<script>alert(1)</script>` sẽ chạy trong trình duyệt nạn nhân. [A03] |
| 4 | CRITICAL | Hardcoded Secret | dòng 53 | `SECRET_KEY` hardcoded trong mã nguồn, tạo exposure nếu code bị lộ hoặc bị reuse ở môi trường khác. [A02] |
| 5 | HIGH | Weak Hash | dòng 57 | `hashlib.md5(...)` là hàm băm yếu cho mật khẩu; attacker có thể crack nhanh bằng rainbow table/bruteforce. [A02] |
| 6 | HIGH | IDOR | dòng 67 | `account_id` từ URL được dùng trực tiếp để lấy account mà không kiểm tra ownership. Attacker chỉ cần đổi ID để xem tài khoản người khác. [A01] |
| 7 | HIGH | SSRF | dòng 98 | `requests.get(url)` với URL do user kiểm soát cho phép gọi tới internal host/metadata, ví dụ `http://169.254.169.254/latest/meta-data/`. [A10] |
| 8 | HIGH | JWT Bypass | dòng 107 | `jwt.decode(..., verify_signature=False)` bỏ qua xác thực chữ ký, nên token forged có thể được chấp nhận như thật. [A07][A02] |
| 9 | MEDIUM | Secret Logging | dòng 118 | Log trực tiếp `password` làm lộ credential vào log files/observability stack. Payload không cần phức tạp: chỉ cần đăng nhập là secret bị ghi lại. [A09][A02] |
| 10 | MEDIUM | Weak Auth | dòng 119 | Hardcoded `admin/admin` tạo backdoor đăng nhập rất dễ đoán. Attacker chỉ cần thử cặp mặc định là vào được. [A07] |

### `main.py` (2 findings)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | HIGH | SQL Injection | dòng 36 | `u_id` được chèn trực tiếp vào query trong vòng lặp. Nếu nguồn `user_ids` bị ảnh hưởng hoặc logic mở rộng sau này nhận input ngoài, payload kiểu `1 OR 1=1` sẽ làm lệch truy vấn và đọc sai dữ liệu. [A03] |
| 2 | MEDIUM | SSRF | dòng 44 | `requests.get("https://slow-api.com/data")` là outbound call cứng, không phải SSRF trực tiếp; nhưng nếu URL này về sau được thay bằng input người dùng thì sẽ mở đường cho SSRF. Hiện tại đây là exposure thấp hơn, chủ yếu là rủi ro thiết kế. [A10] |

### `requirements.txt` (1 finding)

| STT | Mức độ nghiêm trọng | Loại lỗi | Vị trí | Chi tiết mô tả |
|----:|--------------------|----------|--------|----------------|
| 1 | HIGH | Outdated Component | dòng 2-4 | `requests==2.20.0` và các pin cũ làm project exposed tới CVE/bug đã biết nếu version này còn dùng ở production. Dependency stale trong app xử lý HTTP/auth là rủi ro supply-chain rõ ràng. [A06] |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | auth.py, vulnerable_demo.py, main.py, requirements.txt |
| Tổng finding | 13 |
| Mức độ cao nhất | CRITICAL |

### Kết luận

Codebase này đang exposed rất nặng tới injection, auth bypass, secret leakage và SSRF. Nếu đây là code thật chứ không phải demo intentional, mình khuyên chặn release ngay vì có ít nhất vài đường khai thác trực tiếp dẫn tới mất dữ liệu hoặc impersonation.
