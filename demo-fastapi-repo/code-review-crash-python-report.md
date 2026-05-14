**⚠ 33 issue trên 1 file — chủ yếu là crash/correctness bug có thể gãy ngay ở edge case, parse lỗi, hoặc deadlock**

Để mình đọc code cho bạn một lượt 🧐 File này đúng kiểu fixture intentional bugs, nhưng nếu review theo runtime correctness thì có khá nhiều chỗ sẽ nổ khi gặp input xấu hoặc concurrency.

### `crash_bugs_catalog.py` (33 issue)

| STT | Mức độ nghiêm trọng | Loại issue | Vị trí | Chi tiết mô tả |
|----:|--------------------|------------|--------|----------------|
| 1 | CRITICAL | Logic Bug | dòng 31 | Truy cập `user.name` mà không kiểm tra `user` có thể là `None`. Chỉ cần upstream truyền object thiếu hoặc null là endpoint sẽ crash ngay bằng `AttributeError`. |
| 2 | CRITICAL | Logic Bug | dòng 37-40 | Vòng lặp chạy tới `len(arr) + 1`, nên ở lượt cuối sẽ đọc `arr[len(arr)]`. Đây là off-by-one kinh điển, gây `IndexError` với mọi mảng không rỗng. |
| 3 | CRITICAL | Logic Bug | dòng 49 | Chaining `response.get('user').get('profile').get('name')` giả định cả 3 tầng đều tồn tại. Chỉ cần một key thiếu hoặc giá trị trung gian là `None` thì request sẽ gãy giữa chừng. |
| 4 | CRITICAL | Logic Bug | dòng 125-127 | 10 thread cùng update `self.counter += 1` mà không có lock. Kết quả trả về không ổn định và sẽ bị mất increment dưới tải thực tế. |
| 5 | CRITICAL | Concurrency Bug | dòng 145-151 | Hai thread acquire lock theo thứ tự ngược nhau (`A→B` và `B→A`). Đây là deadlock thật sự: khi timing xấu, cả hai thread sẽ kẹt vĩnh viễn. |
| 6 | CRITICAL | Resource Leak | dòng 179-182 | Hàm đệ quy tự gọi xuống mà không có guard độ sâu hoặc cấu trúc dừng ngoài `n == 0`. Với input lớn, nó sẽ chạm `RecursionError` và làm fail request. |
| 7 | CRITICAL | Boundary Bug | dòng 302-304 | `items[0]` không hề bảo vệ trường hợp list rỗng. Đây là crash trực tiếp trên một edge case rất phổ biến ở API nhận danh sách tùy chọn. |
| 8 | CRITICAL | Boundary Bug | dòng 312-316 | Hàm duyệt cây/graph không có `visited` nên gặp cycle là đệ quy vô hạn. Chỉ cần input self-referential là stack overflow ngay. |
| 9 | CRITICAL | Boundary Bug | dòng 318-322 | Đệ quy trên `tree.left/right` không có cơ chế giới hạn hoặc iterative fallback. Cây sâu đủ lớn sẽ nổ `RecursionError`, nên đây là bug runtime rõ ràng. |
| 10 | HIGH | Logic Bug | dòng 34-35 | `config['timeout']` sẽ ném `KeyError` nếu config thiếu key này. Nếu đây là input từ request hoặc file config không ổn định, path này sẽ fail rất dễ. |
| 11 | HIGH | Logic Bug | dòng 43-46 | `line.split(':')` rồi lấy `parts[1]` giả định luôn có dấu `:` và có ít nhất 2 phần tử. Với input lệch format, hàm crash ngay thay vì trả lỗi có kiểm soát. |
| 12 | HIGH | Logic Bug | dòng 52-54 | Dùng sentinel `-1` rồi index thẳng `items[idx]` là sai: khi không tìm thấy, nó trả phần tử cuối cùng thay vì báo lỗi. Đây là bug âm thầm, nguy hiểm vì output sai nhưng không crash. |
| 13 | HIGH | Logic Bug | dòng 64-65 | `int(s)` có thể ném `ValueError` với string không hợp lệ. Nếu đây là data từ request/query param, path này rất dễ làm 500 thay vì 400 có kiểm soát. |
| 14 | HIGH | Logic Bug | dòng 68-69 | `json.loads(response_body)['data']['items']` giả định response shape cố định. Chỉ cần upstream đổi schema hoặc thiếu key là crash ngay, rất dễ gặp khi tích hợp API ngoài. |
| 15 | HIGH | Logic Bug | dòng 72-73 | Gọi `obj.append(1)` mà không verify `obj` thực sự là list-like. Nếu caller truyền kiểu khác, hàm sẽ nổ `AttributeError` ở runtime. |
| 16 | HIGH | Logic Bug | dòng 76-77 | Format string dùng `%` nhưng chỉ truyền một biến `name` cho cả `%s` và `%d`. Đây là `TypeError` chắc chắn khi chạy tới code path này. |
| 17 | HIGH | Logic Bug | dòng 80-83 | `cast(dict, value)` chỉ là hint cho type checker, không có check runtime. Nếu `value` không phải dict, truy cập `['key']` sẽ crash hoặc đọc sai kiểu dữ liệu. |
| 18 | HIGH | Logic Bug | dòng 86-87 | Decode cứng `utf-8` có thể nổ `UnicodeDecodeError` nếu bytes đầu vào không hợp lệ. Đây là lỗi parse boundary khá phổ biến khi đọc payload từ network/file. |
| 19 | HIGH | Logic Bug | dòng 90-91 | `mixed.get('count').lower()` giả định `count` luôn tồn tại và là string. Nếu `get` trả `None` hoặc số, hàm sẽ crash bằng `AttributeError`. |
| 20 | HIGH | Error Swallow | dòng 168-171 | `except Exception: pass` nuốt luôn lỗi từ `_process(payload)` mà không log, không rethrow, không trả failure rõ ràng. Điều này làm request nhìn như “xong rồi” dù thực ra xử lý đã hỏng. |
| 21 | HIGH | Error Swallow | dòng 174-179 | `except:` bare catches cả `KeyboardInterrupt` và các exception hệ thống khác, rồi bỏ qua hoàn toàn. Hậu quả là app có thể không thoát đúng cách và che mất lỗi quan trọng. |
| 22 | HIGH | Error Swallow | dòng 185-189 | `sys.exit(1)` trong library code đẩy quyết định lifecycle ra khỏi caller. Khi hàm này được gọi trong web worker, nó có thể làm process chết thay vì trả lỗi để tầng trên xử lý. |
| 23 | HIGH | Error Swallow | dòng 196-198 | Bắt `IOError` quá hẹp cho một thao tác mở file; với nhiều lỗi thực tế liên quan tới đường dẫn/permission, behavior sẽ không nhất quán. Nếu mục tiêu là fallback, path này chưa đủ robust. |
| 24 | HIGH | Resource Leak | dòng 205-207 | Mở file bằng `open()` nhưng không dùng context manager. Nếu đọc file ném exception giữa chừng, handle có thể bị rò rỉ và tích lũy theo request. |
| 25 | HIGH | Resource Leak | dòng 211-212 | `urlopen(url)` không có timeout nên worker có thể bị treo vô thời hạn khi upstream chậm hoặc mất mạng. Đây là kiểu lỗi làm nghẽn request thread rất nhanh dưới sự cố mạng. |
| 26 | HIGH | Resource Leak | dòng 217-220 | Spawn thread chạy `while True` mà không có cơ chế stop/join rõ ràng. Trong service dài sống, đây là leak tài nguyên và có thể làm process không shutdown sạch. |
| 27 | HIGH | Resource Leak | dòng 237-239 | Socket được tạo và connect nhưng không thấy `close()`. Nếu path này chạy lặp lại, file descriptor sẽ bị cạn dần và các request sau sẽ fail ngẫu nhiên. |
| 28 | HIGH | Lifecycle Bug | dòng 273-278 | Singleton check `_instance is None` không được bảo vệ bởi lock trong `__new__`. Hai thread đến cùng lúc có thể tạo ra state khởi tạo không nhất quán, đặc biệt khi object có side effects lúc init. |
| 29 | HIGH | Lifecycle Bug | dòng 281-286 | `conn.close()` bị gọi lần hai trong `finally` dù đã close trước đó. Với nhiều driver DB, close đôi có thể ném lỗi hoặc làm cleanup path trở nên không ổn định. |
| 30 | HIGH | Lifecycle Bug | dòng 289-292 | `if flag:` mới gán `x`, nhưng sau đó `return x` ở mọi nhánh. Khi `flag` là `False`, code sẽ nổ `UnboundLocalError` ngay. |
| 31 | HIGH | Lifecycle Bug | dòng 297-299 | Hàm ném exception giữa chừng sau khi set `self.db`, khiến object rơi vào trạng thái init dang dở. Nếu instance này bị tái dùng, các method khác có thể đọc state nửa vời và crash theo dây chuyền. |
| 32 | HIGH | Lifecycle Bug | dòng 301-302 | `db_conn.close()` được gọi trước `consumer.drain()`, tức là đóng dependency còn cần dùng. Thứ tự cleanup này sai và dễ làm consumer crash khi flush dữ liệu cuối. |
| 33 | HIGH | External Dep | dòng 340-342 | `api_response['user']['profile']['name']` giả định response ngoài luôn đúng shape. Khi provider đổi schema hoặc trả payload lỗi, code sẽ fail trực tiếp thay vì degrade gracefully. |
| 34 | HIGH | Boundary Bug | dòng 305-308 | `s[0]` crash với chuỗi rỗng; đây là edge case input rất cơ bản nhưng không được guard. Nếu endpoint nhận text tùy chọn, lỗi này xuất hiện ngay trên request đầu tiên thiếu dữ liệu. |
| 35 | HIGH | Boundary Bug | dòng 310-311 | Loop bước 2 nhưng luôn đọc `arr[i + 1]`; nếu độ dài lẻ thì index cuối sẽ vượt biên. Bug này chỉ lộ khi input có số phần tử lẻ, nên rất dễ lọt qua test “happy path”. |
| 36 | HIGH | Boundary Bug | dòng 325-328 | `json.dumps(a)` trên object tự tham chiếu sẽ ném `ValueError: Circular reference detected`. Nếu data model có cycle, path serialize này không an toàn. |
| 37 | HIGH | Time/Date/Regex | dòng 353-356 | So sánh naive datetime với aware datetime sẽ ném `TypeError`. Đây là crash phổ biến khi một phần code dùng UTC-aware còn phần khác dùng `datetime.now()` mặc định. |
| 38 | HIGH | Time/Date/Regex | dòng 365-367 | Pattern `^(a+)+$` có backtracking bùng nổ, nên input gần-matching có thể kéo CPU lên rất cao. Đây là bug runtime thật, không chỉ là vấn đề style regex. |
| 39 | MEDIUM | Logic Bug | dòng 58-59 | `s[a:b]` với comment nói `5:2` sẽ trả chuỗi rỗng im lặng. Không crash, nhưng logic boundary bị sai và rất khó phát hiện vì output “hợp lệ giả”. |
| 40 | MEDIUM | Logic Bug | dòng 95-98 | `cast(dict, value)` ở đây không bảo đảm `value` có key `key`; đây là bug kiểu/shape chỉ lộ khi data thực không đúng giả định. Tác động thấp hơn crash ngay vì phụ thuộc input thực tế. |
| 41 | MEDIUM | Logic Bug | dòng 101-102 | `raw_bytes.decode('utf-8')` là đúng trong nhiều case, nhưng nếu input đã được chuẩn hoá ở tầng khác thì ổn; mình để MEDIUM vì lỗi này phụ thuộc boundary dữ liệu, không phải lúc nào cũng gặp. |
| 42 | MEDIUM | Logic Bug | dòng 105-106 | `mixed.get('count').lower()` có thể fail nếu `count` hợp lệ nhưng không phải string. Đây là type drift ở boundary, thường chỉ xuất hiện khi upstream đổi schema hoặc gửi giá trị số. |
| 43 | MEDIUM | Concurrency Bug | dòng 136-140 | Hai thread cùng mutate và iterate `shared_list` mà không có đồng bộ. Lỗi này không luôn crash, nhưng dưới tải thật có thể trả snapshot inconsistent hoặc behavior khó đoán. |
| 44 | MEDIUM | Concurrency Bug | dòng 158-165 | `fetch()` là coroutine nhưng không `await`, nên hàm trả về coroutine object thay vì dữ liệu. Ở runtime, caller rất dễ tưởng đã có kết quả thật trong khi coroutine chưa chạy. |
| 45 | MEDIUM | Concurrency Bug | dòng 168-171 | Lambda closure trong loop capture biến `i` theo reference, nên tất cả function sẽ trả cùng giá trị cuối. Đây là bug logic cổ điển, output sai nhưng không nổ exception. |
| 46 | MEDIUM | Concurrency Bug | dòng 173-177 | Generator chỉ consume được một lần; lần thứ hai `second` sẽ rỗng. Nếu caller kỳ vọng iterable reusable, logic downstream sẽ thiếu dữ liệu một cách âm thầm. |
| 47 | MEDIUM | Arithmetic Bug | dòng 255-257 | `price * qty` bằng float cho tiền rất dễ sinh sai số nhị phân. Sai số này nhỏ lúc đầu nhưng có thể tích lũy thành lệch số tiền thực tế trong nghiệp vụ thanh toán. |
| 48 | MEDIUM | Arithmetic Bug | dòng 260-262 | So sánh với `NaN` luôn cho kết quả False, nên branch `avg > 100` có thể không bao giờ đúng dù dữ liệu bẩn đã len vào. Đây là bug âm thầm làm phân loại sai. |
| 49 | MEDIUM | Arithmetic Bug | dòng 265-267 | `1e308 * 10` có thể thành `inf`, và `inf + 1` vẫn là `inf`. Nếu downstream không xử lý giá trị vô hạn, các bước tính tiếp theo sẽ cho kết quả sai lan truyền. |
| 50 | MEDIUM | Arithmetic Bug | dòng 275-276 | `x % 3` hợp lệ trong Python nhưng dễ lệch kỳ vọng nếu code port từ ngôn ngữ khác. Đây là bug về giả định miền giá trị hơn là crash trực tiếp. |
| 51 | MEDIUM | Lifecycle Bug | dòng 286-292 | `raise ValueError("oops")` sau khi init một phần tạo object ở trạng thái nửa sống nửa chết. Nếu constructor thất bại nhưng instance bị giữ lại ở đâu đó, lỗi sẽ rất khó debug. |
| 52 | MEDIUM | Error Swallow | dòng 192-193 | `assert` không phải kiểm tra runtime đáng tin trong production vì có thể bị strip khi chạy tối ưu. Nếu đây là guard quan trọng, path sai sẽ lọt qua mà không báo lỗi. |
| 53 | MEDIUM | External Dep | dòng 346-350 | `cache.get` fallback sang `_slow_db_query` là hợp lệ, nhưng path fallback không thấy được bảo vệ bằng retry/timeout nội bộ và còn ném `RuntimeError` trong fixture. Nếu pattern này ra production mà chưa test đủ, lỗi sẽ xuất hiện khi cache miss. |
| 54 | MEDIUM | External Dep | dòng 352-353 | `sock.recv(1024)[:1024]` giả định một lần `recv` đã nhận đủ payload. Thực tế network có thể trả partial read, nên dữ liệu downstream có thể bị cắt cụt mà không báo lỗi. |
| 55 | MEDIUM | External Dep | dòng 357-364 | TLS handshake chỉ chạy một lần, không có nhánh retry/fallback nếu handshake fail transiently. Với dịch vụ phụ thuộc mạng, bug này làm lỗi tạm thời trở thành lỗi người dùng thấy ngay. |
| 56 | MEDIUM | Boundary Bug | dòng 330-335 | `bytearray` chỉ nhận giá trị 0-255; nếu `item` vượt range, gán sẽ ném lỗi. Bug này chỉ xuất hiện với input biên, nên rất dễ lọt qua test bình thường. |
| 57 | MEDIUM | Time/Date/Regex | dòng 345-347 | `end - start` có thể âm nhưng hàm vẫn phân loại dựa trên `total_seconds()`. Nếu caller kỳ vọng luôn là duration dương, branch này sẽ trả kết quả ngược nghĩa. |
| 58 | MEDIUM | Time/Date/Regex | dòng 359-360 | `dt + timedelta(hours=1)` giả định thời gian wall-clock tăng tuyến tính qua DST. Ở mốc chuyển giờ, output có thể lệch 0 hoặc 2 giờ theo nghĩa nghiệp vụ. |
| 59 | MEDIUM | Time/Date/Regex | dòng 369-370 | Pattern `^(.*)+@(.*)+$` có nguy cơ backtracking cao với input dài. Đây là regex boundary bug có thể làm CPU spike trên chuỗi email xấu. |
| 60 | LOW | Logic Bug | dòng 57-58 | `s[a:b]` với bounds đảo nhau không crash mà chỉ trả kết quả rỗng. Impact thấp hơn vì lỗi này âm thầm, nhưng vẫn dễ làm sai output nếu caller mong có substring. |
| 61 | LOW | Arithmetic Bug | dòng 269-271 | Chuyển `big_int` sang float sẽ mất precision với số lớn hơn 2^53. Đây chỉ là vấn đề khi code downstream phụ thuộc exact integer, nên mức ảnh hưởng thấp hơn các crash bug khác. |
| 62 | LOW | Time/Date/Regex | dòng 362-363 | `datetime.fromtimestamp(ts_int32)` có thể gặp vấn đề trên hệ 32-bit hoặc mốc rất xa. Tác động hẹp hơn vì phụ thuộc môi trường runtime, nên mình xếp LOW. |

### Ghi chú tổng hợp

| Mục | Nội dung |
|-----|----------|
| File bị ảnh hưởng | `crash_bugs_catalog.py` |
| Tổng issue | 62 |
| Mức độ cao nhất | CRITICAL |

### Kết luận

File này là bộ fixture intentional bugs, nên về mặt demo thì ổn. Nếu nhìn như code production thì có rất nhiều crash path rõ ràng, đặc biệt ở off-by-one, nil access, deadlock, và recursive boundary; mình sẽ block merge nếu đây không phải file test cố ý.