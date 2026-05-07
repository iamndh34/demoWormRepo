"""
🚨 BẢNG LIỆT KÊ LỖI MONG ĐỢI (EXPECTED FINDINGS)
----------------------------------------------------------------------
| STT | Agent Mục Tiêu         | Loại Lỗi (Error Category)           | Mô Tả Chi Tiết                               |
|-----|------------------------|------------------------------------|----------------------------------------------|
| 1   | perf-profiler          | Async Blocking                     | Dùng 'requests' (sync) trong 'async def'     |
| 2   | perf-profiler          | N+1 Query                          | Truy vấn DB lặp lại trong vòng lặp for       |
| 3   | style-enforcer         | Coding Convention                  | Trộn lẫn camelCase và snake_case             |
| 4   | architect-winston      | Layer Violation                   | Controller gọi trực tiếp DB (bỏ qua Service) |
| 5   | bmad-product-manager   | Missing Features                   | Có TODO chưa hoàn thiện về OAuth2            |
----------------------------------------------------------------------
"""

import asyncio
import requests
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# STYLE: mixed case, global state
global_Db_Conn = None

# PERF: N+1 Query Vulnerability
@app.get("/users/details")
def get_users_details():
    db = sqlite3.connect("users.db")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users")
    user_ids = cursor.fetchall()
    
    results = []
    for (u_id,) in user_ids:
        # N+1: Executing a query inside a loop
        cursor.execute(f"SELECT * FROM profiles WHERE user_id = {u_id}")
        results.append(cursor.fetchone())
    return results

# PERF: Blocking IO inside async function
@app.get("/external-data")
async def get_data():
    # Lỗi: requests.get là sync, sẽ làm treo event loop của FastAPI
    res = requests.get("https://slow-api.com/data") 
    return res.json()

# ARCHITECT: Layer Violation
@app.get("/quick-db")
def quick_db():
    # Lỗi: Logic truy cập dữ liệu nên nằm ở tầng Service/Repository
    return sqlite3.connect("db.sqlite").execute("SELECT * FROM users").fetchall()

# PM/AMELIA: Missing feature placeholder
# TODO: Implement OAuth2 social login with Google and GitHub
def social_login():
    pass
