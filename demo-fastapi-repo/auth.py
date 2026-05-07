"""
🚨 BẢNG LIỆT KÊ LỖI MONG ĐỢI (EXPECTED FINDINGS)
----------------------------------------------------------------------
| STT | Agent Mục Tiêu  | Loại Lỗi (Error Category)      | Mô Tả Chi Tiết                               |
|-----|-----------------|-------------------------------|----------------------------------------------|
| 1   | code-guardian   | Security: SQL Injection        | Nối chuỗi trực tiếp vào query SQL            |
| 2   | code-guardian   | Security: Hardcoded Secret    | Lộ SECRET_KEY ngay trong mã nguồn            |
| 3   | code-guardian   | Security: Timing Attack       | Dùng '==' thay vì hmac.compare_digest        |
| 4   | code-guardian   | Security: Broken Auth         | JWT decode không xác thực chữ ký             |
----------------------------------------------------------------------
"""

import sqlite3
import hmac
import jwt
from fastapi import APIRouter

router = APIRouter()

SECRET_KEY = "super-secret-key-12345"

# SECURITY: SQL Injection
@router.post("/login")
def login(username, password):
    db = sqlite3.connect("users.db")
    cursor = db.cursor()
    # Lỗi: Hacker có thể dùng ' OR 1=1 -- để bypass
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query) 
    return cursor.fetchone()

# SECURITY: Timing Attack
def verify_token(user_token, correct_token):
    # Lỗi: Phơi nhiễm Side-channel timing attack
    if user_token == correct_token:
        return True
    return False

# SECURITY: Insecure JWT
def decode_data(token):
    # Lỗi: verify_signature=False cho phép hacker giả mạo token
    return jwt.decode(token, options={"verify_signature": False})
