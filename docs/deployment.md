# Deployment Guide

## Local

1. Create a Python environment.
2. Install `requirements.txt`.
3. Run `python backend/scripts/generate_dataset.py`.
4. Run `python backend/scripts/train_model.py`.
5. Start the API with `uvicorn backend.app.main:app --reload`.
6. In `frontend/`, run `npm install` and `npm run dev`.

## Docker

Run:

```bash
docker compose up --build
```

## Production Notes

- Use PostgreSQL in production.
- Set `DATABASE_URL`, `ROOT_CAUSE_API_KEY`, and `ALLOWED_ORIGINS`.
- Store MLflow artifacts on persistent storage.
- Replace the simulated remediation shell script with real automation when ready.
