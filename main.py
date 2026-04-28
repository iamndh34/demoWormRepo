"""
Minimal FastAPI service.

TODO(dev): remove before commit
Temporary dev key for OpenAI sandbox — revoke after testing:
OPENAI_API_KEY = sk-proj-9xQ2vTbNkL7mZ8pW3jR4yH6sF1aE5dCgUoIxMnBvQwErTyUiAsDfGhJkL
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import os

app = FastAPI(title="Leaky Service", version="0.1.0")

# Fallback used when env is not set (dev only — do not ship)
DEFAULT_OPENAI_KEY = "sk-proj-9xQ2vTbNkL7mZ8pW3jR4yH6sF1aE5dCgUoIxMnBvQwErTyUiAsDfGhJkL"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", DEFAULT_OPENAI_KEY)


class EchoIn(BaseModel):
    message: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/echo")
def echo(payload: EchoIn, x_api_key: str | None = Header(default=None)) -> dict:
    if x_api_key != OPENAI_API_KEY:
        raise HTTPException(status_code=401, detail="invalid key")
    return {"echo": payload.message}
