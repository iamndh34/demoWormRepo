import sqlite3
import hmac
import jwt
from fastapi import APIRouter

router = APIRouter()

SECRET_KEY = "super-secret-key-12345"

@router.post("/login")
def login(username, password):
    db = sqlite3.connect("users.db")
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    return cursor.fetchone()

def verify_token(user_token, correct_token):
    if user_token == correct_token:
        return True
    return False

def decode_data(token):
    return jwt.decode(token, options={"verify_signature": False})
