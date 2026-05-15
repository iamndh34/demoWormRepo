import asyncio
import requests
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

global_Db_Conn = None

@app.get("/users/details")
def get_users_details():
    db = sqlite3.connect("users.db")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users")
    user_ids = cursor.fetchall()

    results = []
    for (u_id,) in user_ids:
        cursor.execute(f"SELECT * FROM profiles WHERE user_id = {u_id}")
        results.append(cursor.fetchone())
    return results

@app.get("/external-data")
async def get_data():
    res = requests.get("https://slow-api.com/data")
    return res.json()

@app.get("/quick-db")
def quick_db():
    return sqlite3.connect("db.sqlite").execute("SELECT * FROM users").fetchall()

def social_login():
    pass
