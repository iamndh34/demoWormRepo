import os
import pickle
import sqlite3
import subprocess
import hashlib
import logging
import yaml
import requests
import jwt
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/user")
def get_user(username: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()


@app.get("/ping")
def ping_host(host: str):
    result = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return {"output": result.decode()}


@app.get("/greet", response_class=HTMLResponse)
def greet(name: str):
    return f"<html><body><h1>Hello, {name}!</h1></body></html>"


SECRET_KEY = "supersecret123"
API_TOKEN = "AKIAIOSFODNN7EXAMPLE"

def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


@app.get("/account/{account_id}")
def get_account(account_id: int):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM accounts WHERE id = {account_id}")
    return cursor.fetchall()


@app.post("/load")
async def load_data(request: Request):
    body = await request.body()
    obj = pickle.loads(body)
    return {"loaded": str(obj)}


DEBUG = True

@app.post("/config")
async def load_config(request: Request):
    body = await request.body()
    config = yaml.load(body, Loader=yaml.Loader)
    return {"config": config}


@app.get("/fetch")
def fetch_url(url: str):
    response = requests.get(url)
    return {"content": response.text}


@app.get("/whoami")
def whoami(token: str):
    payload = jwt.decode(token, options={"verify_signature": False})
    return {"user": payload.get("username")}


logging.basicConfig(level=logging.INFO)

@app.post("/login")
def login(username: str, password: str):
    logging.info(f"Login attempt: user={username}, password={password}")
    if username == "admin" and password == "admin":
        return {"status": "ok"}
    return {"status": "fail"}
