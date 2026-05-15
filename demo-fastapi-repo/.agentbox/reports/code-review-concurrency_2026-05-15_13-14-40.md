# code-review-concurrency — saved by agentbox --save

Generated: 2026-05-15T06:15:00Z

**⚠ 4 issue trên 3 file — có 1 bug crash rõ ràng và 3 lỗi error handling/logic cần sửa trước khi merge**

Chào bạn, mình đọc nhanh theo hướng correctness/runtime crash risk nhé.

### `logic.py` (1 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | CRITICAL | Logic Bug | dòng 9-11 | Vòng lặp chạy tới `len(numbers) + 1` nên lần cuối sẽ truy cập `numbers[len(numbers)]`, chắc chắn out of range khi list không rỗng. Với input rỗng thì hàm còn chủ động crash bằng `0 / 0`, nên path này không bao giờ trả về kết quả hợp lệ. |

### `main.py` (2 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | HIGH | Error Swallow | dòng 35-38 | `sqlite3.connect(...)` và `cursor.fetchone()` được gọi trong vòng lặp mà không có cleanup rõ ràng cho connection. Nếu có exception giữa chừng, hàm trả về sớm mà không đóng DB handle, dễ gây leak tài nguyên và lỗi lặt vặt khi tải cao. |
| 2 | MEDIUM | Missing Feature | dòng 54-55 | `social_login()` chỉ là stub `pass` nhưng lại được để như một phần chức năng của app. Nếu route hoặc caller nào đó bắt đầu dùng nó, hệ thống sẽ trả về hành vi “thành công giả” thay vì báo chưa triển khai, rất dễ che mất feature gap trong prod. |

### `errors.py` (1 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | HIGH | Error Swallow | dòng 13-17 | `except:` bắt mọi exception rồi `pass`, nên cả lỗi thật lẫn `KeyboardInterrupt`/`SystemExit` đều bị nuốt mất. Điều này làm lỗi production biến mất không dấu vết, và còn khiến quá trình dừng khẩn cấp không hoạt động đúng. |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | logic.py, main.py, errors.py |
| Tổng issue | 4 |
| Mức độ cao nhất | CRITICAL |

### Kết luận

Đây chưa phải code sạch để merge production: có 1 bug crash chắc chắn ở `logic.py`, cộng thêm các lỗi error handling có thể làm che mất failure thật hoặc gây leak tài nguyên. Mình khuyên fix các issue mức cao trước rồi mới merge.
**⚠ 5 issue trên 3 file — chủ yếu là lỗi logic có thể gây crash hoặc trả kết quả sai**

### `logic.py` (1 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | CAO | Logic Bug | dòng 7-10 | Vòng lặp chạy tới `len(numbers) + 1`, nên lần cuối sẽ truy cập vượt biên `numbers[i]`. Với input không rỗng, hàm này sẽ ném `IndexError` thay vì trả kết quả trung bình. |

### `errors.py` (1 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | CAO | Error Swallow | dòng 15-18 | `except:` nuốt toàn bộ exception, כולל cả `KeyboardInterrupt` và `SystemExit`. Khi `open()` hoặc `read()` fail, lỗi bị bỏ qua hoàn toàn nên caller không biết file xử lý thất bại vì lý do gì. |

### `main.py` (3 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | CAO | Async Blocking | dòng 24-27 | `requests.get()` là call đồng bộ nhưng lại nằm trong `async def`. Trong FastAPI, nó sẽ chặn event loop, làm các request khác bị treo theo khi endpoint này chậm hoặc upstream timeout. |
| 2 | TRUNG BÌNH | N+1 Query | dòng 13-21 | Hàm lấy danh sách user rồi query thêm một lần cho từng `user_id`. Với dữ liệu lớn, số query tăng tuyến tính theo số user và dễ làm endpoint chậm bất thường; đây là bug correctness ở mức vận hành vì kết quả phụ thuộc mạnh vào kích thước dữ liệu. |
| 3 | TRUNG BÌNH | Layer Violation | dòng 30-32 | Endpoint đang mở connection và query DB trực tiếp ngay trong handler. Điều này làm logic truy cập dữ liệu bị dính chặt vào controller, khó kiểm soát transaction/error handling và dễ tạo hành vi không nhất quán giữa các endpoint. |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | logic.py, errors.py, main.py |
| Tổng issue | 5 |
| Mức độ cao nhất | CAO |

### Kết luận

Code này chưa clean ở mức production: có 2 lỗi mức cao có thể gây crash hoặc làm treo request, cộng thêm vài vấn đề logic/kiến trúc ảnh hưởng trực tiếp tới hành vi runtime. Mình khuyên nên fix trước khi merge, nhất là `logic.py`, `errors.py`, và endpoint async trong `main.py`.
**⚠ 8 issue trên 4 file — chủ yếu là crash/logic bug ở edge case và error handling**

### `main.py` (3 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | CAO | Async Blocking | dòng 31-33 | Endpoint là `async def` nhưng gọi `requests.get()` đồng bộ, nên sẽ chặn event loop của FastAPI trong lúc chờ network. Khi upstream chậm, toàn bộ worker có thể bị nghẽn thay vì chỉ request này bị chậm. |
| 2 | CAO | N+1 Query | dòng 20-25 | Hàm lấy toàn bộ `user_ids` rồi query từng profile trong vòng lặp, tạo mẫu N+1 rõ ràng. Với số user tăng lên, số round-trip DB tăng tuyến tính và dễ làm endpoint chậm bất thường hoặc timeout. |
| 3 | TRUNG BÌNH | Missing Feature | dòng 38-39 | `social_login()` chỉ là stub `pass` nhưng lại được để như một phần của app. Nếu route hoặc flow nào đó bắt đầu gọi vào đây, nó sẽ trả về `None` thay vì hành vi OAuth2 thật, khiến feature trông như có nhưng thực tế không hoạt động. |

### `auth.py` (2 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | CAO | SQL Injection | dòng 14-18 | Query được dựng bằng f-string từ `username` và `password`, nên input độc hại có thể làm thay đổi cấu trúc SQL. Đây là lỗi correctness nghiêm trọng vì một chuỗi bất thường là đủ để bypass logic đăng nhập hoặc làm query fail ngoài ý muốn. |
| 2 | CAO | Broken Auth | dòng 24-26 | `jwt.decode(..., options={"verify_signature": False})` bỏ qua xác thực chữ ký, nên payload giả mạo vẫn được chấp nhận như token hợp lệ. Điều này phá luôn giả định tin cậy của toàn bộ luồng auth phía sau. |

### `crash_bugs_catalog.py` (2 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | CAO | Logic Bug | dòng 275-276 | `assert` đang được dùng để bảo vệ dữ liệu đầu vào, nhưng trong Python chạy với `-O` thì assert bị strip hoàn toàn. Khi đó check biến mất và hàm có thể đi tiếp với `user_data is None`, dẫn tới crash ở chỗ khác khó truy vết hơn. |
| 2 | CAO | Error Swallow | dòng 31-34 | `except Exception: pass` nuốt toàn bộ lỗi từ `_process(payload)` và trả về im lặng. Caller sẽ không biết request thất bại vì lý do gì, nên bug thật bị che mất và hệ thống có thể tiếp tục với trạng thái sai. |

### `vulnerable_demo.py` (1 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | CAO | Broken Auth | dòng 92-94 | JWT được decode với `verify_signature=False`, nên token không cần chữ ký hợp lệ vẫn được chấp nhận. Đây là lỗi logic auth trực tiếp: dữ liệu đầu vào không còn được xác thực, nên mọi quyết định dựa trên payload đều không đáng tin. |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | main.py, auth.py, crash_bugs_catalog.py, vulnerable_demo.py |
| Tổng issue | 8 |
| Mức độ cao nhất | CAO |

### Kết luận

PR này có vài lỗi correctness đáng chú ý, chủ yếu quanh auth và error handling; riêng các chỗ JWT bỏ verify signature và SQL dựng bằng chuỗi nên mình xem là cần xử lý trước khi merge. Phần còn lại nhìn chung là fixture/demo code, nhưng nếu đây là code production thì mình sẽ block merge cho tới khi các issue cao được dọn xong.
