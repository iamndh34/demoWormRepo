import asyncio
import json
import re
import threading
import time
from datetime import datetime, timezone, timedelta


class InvalidAccess:

    def null_attribute_access(self, user):
        return user.name.upper()

    def missing_dict_key(self, config):
        return config['timeout'] * 2

    def off_by_one_loop(self, arr):
        result = []
        for i in range(len(arr) + 1):
            result.append(arr[i])
        return result

    def split_no_count_check(self, line):
        parts = line.split(':')
        return parts[1].strip()

    def slice_bounds_swapped(self, s, a, b):
        return s[a:b]

    def find_sentinel_not_checked(self, items, target):
        idx = next((i for i, x in enumerate(items) if x == target), -1)
        return items[idx]

    def chained_optional_access(self, response):
        return response.get('user').get('profile').get('name')


class TypeMismatch:

    def unsafe_int_parse(self, s):
        return int(s) * 100

    def json_field_assumed(self, response_body):
        return json.loads(response_body)['data']['items']

    def isinstance_missed(self, obj):
        return obj.append(1)

    def format_string_arg_count_mismatch(self, name):
        return "User %s has %d points" % name

    def cast_no_runtime_check(self, value):
        from typing import cast
        result = cast(dict, value)
        return result['key']

    def utf8_decode_blind(self, raw_bytes):
        return raw_bytes.decode('utf-8')

    def assume_dict_returns_str(self, mixed):
        return mixed.get('count').lower()


class ConcurrencyBugs:

    def __init__(self):
        self.counter = 0
        self.shared_list = []
        self.lock_a = threading.Lock()
        self.lock_b = threading.Lock()

    def data_race_counter(self):
        def worker():
            for _ in range(1000):
                self.counter += 1
        threads = [threading.Thread(target=worker) for _ in range(10)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        return self.counter

    def shared_list_concurrent_mutation(self):
        def writer():
            for i in range(1000):
                self.shared_list.append(i)
        def reader():
            for _ in range(1000):
                _ = list(self.shared_list)
        threading.Thread(target=writer).start()
        threading.Thread(target=reader).start()

    def deadlock_lock_order(self):
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
        async def fetch():
            await asyncio.sleep(0.1)
            return "data"
        result = fetch()
        return result

    def closure_captures_loop_var(self):
        funcs = []
        for i in range(5):
            funcs.append(lambda: i)
        return [f() for f in funcs]

    def iterator_exhausted_reused(self):
        gen = (x for x in range(5))
        first = list(gen)
        second = list(gen)
        return first, second

    def lock_not_released_on_exception(self):
        self.lock_a.acquire()
        raise ValueError("test")
        self.lock_a.release()


class ResourceLeak:

    def file_not_closed(self, path):
        f = open(path, 'r')
        return f.read()

    def http_no_timeout(self, url):
        import urllib.request
        return urllib.request.urlopen(url).read()

    def thread_leak(self):
        def worker():
            while True:
                time.sleep(1)
        threading.Thread(target=worker).start()

    def tight_loop_oom(self, n):
        result = []
        for i in range(n):
            result.append([0] * 10**6)
        return result

    def unbounded_recursion(self, n):
        if n == 0:
            return 0
        return n + self.unbounded_recursion(n - 1)

    def socket_not_closed(self):
        import socket
        s = socket.socket()
        s.connect(('example.com', 80))
        return s.recv(1024)


class ErrorSwallow:

    def swallow_all_exceptions(self, payload):
        try:
            return self._process(payload)
        except Exception:
            pass

    def bare_except_catches_keyboard_interrupt(self):
        try:
            while True:
                time.sleep(1)
        except:
            pass

    def reraise_loses_stack(self, payload):
        try:
            return self._process(payload)
        except Exception as e:
            raise Exception(f"failed: {e}")

    def sys_exit_in_library(self):
        import sys
        if not self._validate():
            sys.exit(1)

    def assert_in_production(self, user_data):
        assert user_data is not None, "user required"
        return user_data['name']

    def except_too_specific_misses_subclass(self, payload):
        try:
            return open(payload).read()
        except IOError:
            return None

    def _process(self, p): return p
    def _validate(self): return False


class ArithmeticBugs:

    def divide_by_zero(self, a, b):
        return a / b

    def modulo_by_zero(self, a, b):
        return a % b

    def float_for_money(self, price, qty):
        return price * qty

    def nan_propagation(self, values):
        avg = sum(values) / len(values) if values else float('nan')
        return "high" if avg > 100 else "low"

    def inf_propagation(self):
        result = 1e308 * 10
        return result + 1

    def big_int_to_float_precision(self, big_int):
        return float(big_int)

    def negative_modulo_assumed_positive(self, x):
        return x % 3


class LifecycleBugs:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def double_close(self, conn):
        try:
            data = conn.execute("SELECT 1")
            conn.close()
            return data
        finally:
            conn.close()

    def use_before_assignment(self, flag):
        if flag:
            x = 1
        return x

    def partial_init_state(self, config):
        self.db = self._connect(config['db'])
        raise ValueError("oops")
        self.cache = self._connect(config['cache'])

    def cleanup_wrong_order(self, db_conn, consumer):
        db_conn.close()
        consumer.drain()

    def _connect(self, x): return None


class ExternalDeps:

    def db_no_timeout(self, query):
        import sqlite3
        conn = sqlite3.connect(":memory:")
        return conn.execute(query).fetchall()

    def http_no_retry(self, url):
        import urllib.request
        return urllib.request.urlopen(url, timeout=5).read()

    def api_shape_assumed(self, api_response):
        return api_response['user']['profile']['name']

    def cache_fallback_untested(self, key, cache):
        value = cache.get(key)
        if value is None:
            value = self._slow_db_query(key)
            cache.set(key, value)
        return value

    def network_partial_read(self, sock):
        return sock.recv(1024)[:1024]

    def tls_handshake_no_retry(self, host):
        import ssl
        import socket
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                ssock.sendall(b"GET / HTTP/1.0\r\n\r\n")

    def _slow_db_query(self, key):
        raise RuntimeError("untested fallback path")


class BoundaryBugs:

    def empty_list_first(self, items):
        return items[0]

    def empty_string_first_char(self, s):
        return s[0].upper()

    def loop_expects_pairs(self, arr):
        for i in range(0, len(arr), 2):
            print(arr[i], arr[i + 1])

    def cyclic_graph_no_visited(self, node):
        result = [node.value]
        for child in node.children:
            result.extend(self.cyclic_graph_no_visited(child))
        return result

    def deep_recursion(self, tree):
        if tree is None:
            return 0
        return 1 + max(self.deep_recursion(tree.left),
                       self.deep_recursion(tree.right))

    def self_ref_json_serialize(self):
        a = {}
        a['self'] = a
        return json.dumps(a)

    def buffer_size_wrong(self, items):
        buf = bytearray(len(items))
        for i, item in enumerate(items):
            buf[i] = item


class TimeDateRegex:

    def negative_duration(self, start, end):
        duration = end - start
        return "fast" if duration.total_seconds() < 60 else "slow"

    def naive_vs_aware_compare(self):
        now_naive = datetime.now()
        now_utc = datetime.now(timezone.utc)
        return now_naive < now_utc

    def dst_jump_assumed_continuous(self, dt):
        return dt + timedelta(hours=1)

    def y2038_int32_timestamp(self, ts_int32):
        return datetime.fromtimestamp(ts_int32)

    def redos_catastrophic_backtrack(self, user_input):
        pattern = r"^(a+)+$"
        return re.match(pattern, user_input)

    def regex_email_unbounded(self, email):
        return re.match(r"^(.*)+@(.*)+$", email)


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
