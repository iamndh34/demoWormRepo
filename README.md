# Leaky Service

Minimal FastAPI demo.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoints

- `GET /health` — liveness
- `POST /echo` — requires `X-API-Key` header
