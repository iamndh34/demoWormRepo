"""
Crash Bugs Catalog — fixture cho code-review crash-detection agent.

WARNING: File này CHỨA LỖI INTENTIONAL. KHÔNG chạy logic bên trong
ở production. Code-review agent đọc file này như input để verify
khả năng phát hiện các pattern crash phổ biến.

Mỗi class = 1 nhóm lỗi (theo BUILD_AGENT_FLOW.md crash taxonomy).
Mỗi method = 1 pattern cụ thể, kèm tag [SEVERITY] trong comment.

10 nhóm:
  1. InvalidAccess      — null deref, index out of bounds, off-by-one
  2. TypeMismatch       — type assertion, JSON parse, format string
  3. ConcurrencyBugs    — data race, deadlock, async/await missing
  4. ResourceLeak       — file/thread leak, OOM, recursion
  5. ErrorSwallow       — try/except/pass, sys.exit, lost stack
  6. ArithmeticBugs     — div-by-zero, overflow, NaN/Inf, float money
  7. LifecycleBugs      — singleton race, use-before-init, double-close
  8. ExternalDeps       — no timeout, no retry, response shape assumed
  9. BoundaryBugs       — empty/single input, cycle, deep recursion
 10. TimeDateRegex      — DST jump, timezone naive, ReDoS

Cách dùng với agent:
  agentbox <crash-review-agent-slug> "review file demos/crash_bugs_catalog.py"
"""

# pylint: disable=all
# flake8: noqa
# ruff: noqa
# Intentional bugs — disable linters

import asyncio
import json
import re
import threading
import time
from datetime import datetime, timezone, timedelta


# =============================================================================
# Group 1 — Truy cập giá trị không hợp lệ
# =============================================================================
class InvalidAccess:
    """Null deref, index OOB, off-by-one, magic sentinel."""

    def null_attribute_access(self, user):
        # [CRITICAL] AttributeError nếu user None
        return user.name.upper()

    def missing_dict_key(self, config):
        # [HIGH] KeyError nếu config không có 'timeout'
        return config['timeout'] * 2

    def off_by_one_loop(self, arr):
        # [CRITICAL] IndexError ở i == len(arr)
        result = []
        for i in range(len(arr) + 1):
            result.append(arr[i])
        return result

    def split_no_count_check(self, line):
        # [HIGH] IndexError nếu line không có ':'
        parts = line.split(':')
        return parts[1].strip()

    def slice_bounds_swapped(self, s, a, b):
        # [LOW] s[5:2] silent empty — không crash nhưng logic sai
        return s[a:b]

    def find_sentinel_not_checked(self, items, target):
        # [HIGH] items[-1] khi find fail → trả nhầm last item
        idx = next((i for i, x in enumerate(items) if x == target), -1)
        return items[idx]

    def chained_optional_access(self, response):
        # [CRITICAL] response.get('user') có thể None
        return response.get('user').get('profile').get('name')


# =============================================================================
# Group 2 — Type / parse / cast sai
# =============================================================================
class TypeMismatch:
    """Type assertion, JSON parse, format string mismatches."""

    def unsafe_int_parse(self, s):
        # [HIGH] ValueError nếu s không parse được
        return int(s) * 100

    def json_field_assumed(self, response_body):
        # [HIGH] KeyError nếu 'data' không có
        return json.loads(response_body)['data']['items']

    def isinstance_missed(self, obj):
        # [HIGH] AttributeError nếu obj không phải list
        return obj.append(1)

    def format_string_arg_count_mismatch(self, name):
        # [HIGH] TypeError: not enough arguments
        return "User %s has %d points" % name

    def cast_no_runtime_check(self, value):
        # [MEDIUM] typing.cast là hint, không enforce runtime
        from typing import cast
        result = cast(dict, value)
        return result['key']

    def utf8_decode_blind(self, raw_bytes):
        # [HIGH] UnicodeDecodeError với invalid bytes
        return raw_bytes.decode('utf-8')

    def assume_dict_returns_str(self, mixed):
        # [MEDIUM] dict.get() có thể trả None hoặc kiểu khác
        return mixed.get('count').lower()


# =============================================================================
# Group 3 — Concurrency
# =============================================================================
class ConcurrencyBugs:
    """Data race, deadlock, async/await missing, closure capture."""

    def __init__(self):
        self.counter = 0
        self.shared_list = []
        self.lock_a = threading.Lock()
        self.lock_b = threading.Lock()

    def data_race_counter(self):
        # [HIGH] counter += 1 không atomic
        def worker():
            for _ in range(1000):
                self.counter += 1
        threads = [threading.Thread(target=worker) for _ in range(10)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        return self.counter  # < 10000

    def shared_list_concurrent_mutation(self):
        # [HIGH] Append + iterate concurrent
        def writer():
            for i in range(1000):
                self.shared_list.append(i)
        def reader():
            for _ in range(1000):
                _ = list(self.shared_list)
        threading.Thread(target=writer).start()
        threading.Thread(target=reader).start()

    def deadlock_lock_order(self):
        # [CRITICAL] t1 lock A→B, t2 lock B→A
        def thread1():
            with self.lock_a:
                time.sleep(0.01)
                with self.lock_b:
                    pass
        def thread2():
            with self.lock_b:
                time.sleep(0.01)
                with self.lock_a:
                    pass
        threading.Thread(target=thread1).start()
        threading.Thread(target=thread2).start()

    async def missing_await(self):
        # [HIGH] Coroutine never awaited → silent fail
        async def fetch():
            await asyncio.sleep(0.1)
            return "data"
        result = fetch()  # quên await
        return result  # trả Coroutine, không phải string

    def closure_captures_loop_var(self):
        # [MEDIUM] Tất cả func đều trả 4 (last i)
        funcs = []
        for i in range(5):
            funcs.append(lambda: i)
        return [f() for f in funcs]

    def iterator_exhausted_reused(self):
        # [MEDIUM] Generator chỉ iterate được 1 lần
        gen = (x for x in range(5))
        first = list(gen)
        second = list(gen)  # rỗng
        return first, second

    def lock_not_released_on_exception(self):
        # [HIGH] Quên `with` → lock không release nếu raise
        self.lock_a.acquire()
        raise ValueError("test")
        self.lock_a.release()  # never reached


# =============================================================================
# Group 4 — Resource leak / exhaustion
# =============================================================================
class ResourceLeak:
    """File/connection/thread leak, OOM, infinite recursion."""

    def file_not_closed(self, path):
        # [HIGH] Không dùng `with` → file handle leak
        f = open(path, 'r')
        return f.read()

    def http_no_timeout(self, url):
        # [HIGH] urlopen không timeout → hang
        import urllib.request
        return urllib.request.urlopen(url).read()

    def thread_leak(self):
        # [HIGH] Daemon=False + infinite loop → main không exit
        def worker():
            while True:
                time.sleep(1)
        threading.Thread(target=worker).start()

    def tight_loop_oom(self, n):
        # [HIGH] Allocate 1M ints mỗi iter → memory grow
        result = []
        for i in range(n):
            result.append([0] * 10**6)
        return result

    def unbounded_recursion(self, n):
        # [CRITICAL] RecursionError ở n quá lớn (default limit 1000)
        if n == 0:
            return 0
        return n + self.unbounded_recursion(n - 1)

    def socket_not_closed(self):
        # [HIGH] Socket open không close → FD exhaust
        import socket
        s = socket.socket()
        s.connect(('example.com', 80))
        return s.recv(1024)


# =============================================================================
# Group 5 — Error handling
# =============================================================================
class ErrorSwallow:
    """try/except/pass, raise mất stack, sys.exit ngoài main."""

    def swallow_all_exceptions(self, payload):
        # [HIGH] except Exception nuốt cả KeyboardInterrupt? Không, nhưng
        # bare except thì có. Vẫn nuốt logic errors quan trọng.
        try:
            return self._process(payload)
        except Exception:
            pass

    def bare_except_catches_keyboard_interrupt(self):
        # [HIGH] bare except: bắt cả Ctrl+C
        try:
            while True:
                time.sleep(1)
        except:  # noqa: E722
            pass

    def reraise_loses_stack(self, payload):
        # [MEDIUM] Tạo Exception mới mất original traceback
        try:
            return self._process(payload)
        except Exception as e:
            raise Exception(f"failed: {e}")

    def sys_exit_in_library(self):
        # [HIGH] Library KHÔNG nên gọi sys.exit; raise Exception cho caller decide
        import sys
        if not self._validate():
            sys.exit(1)

    def assert_in_production(self, user_data):
        # [MEDIUM] python -O strip assert → check biến mất
        assert user_data is not None, "user required"
        return user_data['name']

    def except_too_specific_misses_subclass(self, payload):
        # [MEDIUM] Bắt IOError nhưng caller có thể raise OSError subclass
        try:
            return open(payload).read()
        except IOError:
            return None
        # PermissionError (subclass của OSError) không phải IOError trong Py3?

    def _process(self, p): return p
    def _validate(self): return False


# =============================================================================
# Group 6 — Arithmetic
# =============================================================================
class ArithmeticBugs:
    """Division by zero, overflow, NaN/Inf, decimal precision."""

    def divide_by_zero(self, a, b):
        # [HIGH] ZeroDivisionError
        return a / b

    def modulo_by_zero(self, a, b):
        # [HIGH] ZeroDivisionError
        return a % b

    def float_for_money(self, price, qty):
        # [HIGH] 0.1 + 0.2 = 0.30000000000000004 → tiền sai
        return price * qty

    def nan_propagation(self, values):
        # [MEDIUM] NaN comparison luôn False → logic broken
        avg = sum(values) / len(values) if values else float('nan')
        return "high" if avg > 100 else "low"

    def inf_propagation(self):
        # [MEDIUM] Overflow → Inf, propagate downstream
        result = 1e308 * 10
        return result + 1  # vẫn Inf

    def big_int_to_float_precision(self, big_int):
        # [LOW] int > 2^53 mất precision khi cast sang float
        return float(big_int)

    def negative_modulo_assumed_positive(self, x):
        # [MEDIUM] -7 % 3 = 2 trong Python (math), -1 trong C → assume sai
        return x % 3


# =============================================================================
# Group 7 — Lifecycle / init / cleanup
# =============================================================================
class LifecycleBugs:
    """Singleton race, use-before-init, double-close, cleanup order."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # [HIGH] Singleton race: 2 thread cùng vào nhánh None
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def double_close(self, conn):
        # [HIGH] Close 2 lần → connection error
        try:
            data = conn.execute("SELECT 1")
            conn.close()
            return data
        finally:
            conn.close()  # second close

    def use_before_assignment(self, flag):
        # [HIGH] UnboundLocalError nếu flag False
        if flag:
            x = 1
        return x

    def partial_init_state(self, config):
        # [MEDIUM] Raise giữa __init__ → object ở state lỗi
        self.db = self._connect(config['db'])
        raise ValueError("oops")
        self.cache = self._connect(config['cache'])  # never reached

    def cleanup_wrong_order(self, db_conn, consumer):
        # [HIGH] Close DB trước consumer drain → consumer crash
        db_conn.close()
        consumer.drain()

    def _connect(self, x): return None


# =============================================================================
# Group 8 — External dependency
# =============================================================================
class ExternalDeps:
    """Timeout missing, retry missing, response shape assumed."""

    def db_no_timeout(self, query):
        # [HIGH] sqlite3 default không có timeout → hang khi lock
        import sqlite3
        conn = sqlite3.connect(":memory:")
        return conn.execute(query).fetchall()

    def http_no_retry(self, url):
        # [HIGH] 1 lần fail → cascading
        import urllib.request
        return urllib.request.urlopen(url, timeout=5).read()

    def api_shape_assumed(self, api_response):
        # [HIGH] Assume 3 levels nested
        return api_response['user']['profile']['name']

    def cache_fallback_untested(self, key, cache):
        # [HIGH] Cache miss path không test
        value = cache.get(key)
        if value is None:
            value = self._slow_db_query(key)
            cache.set(key, value)
        return value

    def network_partial_read(self, sock):
        # [HIGH] recv(N) có thể trả < N bytes
        return sock.recv(1024)[:1024]

    def tls_handshake_no_retry(self, host):
        # [MEDIUM] Handshake fail là dead
        import ssl
        import socket
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                ssock.sendall(b"GET / HTTP/1.0\r\n\r\n")

    def _slow_db_query(self, key):
        raise RuntimeError("untested fallback path")


# =============================================================================
# Group 9 — Boundary / edge case
# =============================================================================
class BoundaryBugs:
    """Empty/single input, cycle, recursion limit, self-ref."""

    def empty_list_first(self, items):
        # [CRITICAL] IndexError nếu items rỗng
        return items[0]

    def empty_string_first_char(self, s):
        # [HIGH] IndexError nếu s == ''
        return s[0].upper()

    def loop_expects_pairs(self, arr):
        # [HIGH] IndexError nếu len(arr) odd
        for i in range(0, len(arr), 2):
            print(arr[i], arr[i + 1])

    def cyclic_graph_no_visited(self, node):
        # [CRITICAL] Stack overflow nếu graph có cycle
        result = [node.value]
        for child in node.children:
            result.extend(self.cyclic_graph_no_visited(child))
        return result

    def deep_recursion(self, tree):
        # [CRITICAL] RecursionError với tree sâu
        if tree is None:
            return 0
        return 1 + max(self.deep_recursion(tree.left),
                       self.deep_recursion(tree.right))

    def self_ref_json_serialize(self):
        # [HIGH] ValueError: Circular reference detected
        a = {}
        a['self'] = a
        return json.dumps(a)

    def buffer_size_wrong(self, items):
        # [MEDIUM] bytearray slot 0-255; item > 255 → OverflowError
        buf = bytearray(len(items))
        for i, item in enumerate(items):
            buf[i] = item


# =============================================================================
# Group 10 — Time / date / regex
# =============================================================================
class TimeDateRegex:
    """Date overflow, DST, timezone mismatch, ReDoS."""

    def negative_duration(self, start, end):
        # [MEDIUM] end < start → negative timedelta, comparison sai
        duration = end - start
        return "fast" if duration.total_seconds() < 60 else "slow"

    def naive_vs_aware_compare(self):
        # [HIGH] TypeError: can't compare naive vs aware
        now_naive = datetime.now()
        now_utc = datetime.now(timezone.utc)
        return now_naive < now_utc

    def dst_jump_assumed_continuous(self, dt):
        # [MEDIUM] +1 hour khi DST jump → 0 hoặc 2 hour wall-clock
        return dt + timedelta(hours=1)

    def y2038_int32_timestamp(self, ts_int32):
        # [LOW] Timestamp > 2^31 fail trên system 32-bit
        return datetime.fromtimestamp(ts_int32)

    def redos_catastrophic_backtrack(self, user_input):
        # [HIGH] ReDoS: "aaaa...!" với pattern này → CPU 100%
        pattern = r"^(a+)+$"
        return re.match(pattern, user_input)

    def regex_email_unbounded(self, email):
        # [MEDIUM] Pattern (.*)+ exponential backtrack
        return re.match(r"^(.*)+@(.*)+$", email)


# =============================================================================
# Smoke runner — verify file syntax OK. KHÔNG chạy logic.
# =============================================================================
if __name__ == "__main__":
    catalog = {
        "1. InvalidAccess":   InvalidAccess,
        "2. TypeMismatch":    TypeMismatch,
        "3. ConcurrencyBugs": ConcurrencyBugs,
        "4. ResourceLeak":    ResourceLeak,
        "5. ErrorSwallow":    ErrorSwallow,
        "6. ArithmeticBugs":  ArithmeticBugs,
        "7. LifecycleBugs":   LifecycleBugs,
        "8. ExternalDeps":    ExternalDeps,
        "9. BoundaryBugs":    BoundaryBugs,
        "10. TimeDateRegex":  TimeDateRegex,
    }
    total = 0
    for name, cls in catalog.items():
        methods = [m for m in dir(cls) if not m.startswith('_')]
        total += len(methods)
        print(f"{name:25s}: {len(methods)} bug patterns")
    print(f"\nTotal: {total} crash-prone patterns across 10 groups")
