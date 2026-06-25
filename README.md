# PredictiveOps AI

PredictiveOps AI is a production-style incident prediction and self-healing platform that ingests system metrics, predicts failure risk, explains likely root cause, and simulates automated remediation.

## What it does

- Generates synthetic system telemetry for CPU, memory, disk, latency, traffic, errors, and response time
- Trains and compares Random Forest, XGBoost, and Logistic Regression models
- Selects the best model automatically using macro F1 and ROC AUC
- Persists metrics, incidents, and actions in PostgreSQL
- Performs root-cause analysis with an LLM-backed analyzer and heuristic fallback
- Surfaces the full workflow in a React + Recharts dashboard

## Stack

- Backend: FastAPI, Python, SQLAlchemy
- ML: scikit-learn, XGBoost, Pandas, NumPy, MLflow, DVC
- Frontend: React, TypeScript, Tailwind CSS, Recharts
- Database: PostgreSQL
- Automation: GitHub Actions, shell scripts
- Containerization: Docker

## Project Layout

- `backend/` API, persistence, and orchestration
- `frontend/` dashboard UI
- `ml/` training, inference, and synthetic data generation
- `database/` schema
- `workflows/` automation scripts
- `docker/` container builds
- `tests/` unit and integration coverage
- `docs/` architecture and deployment notes

## Quick Start

```bash
python backend/scripts/generate_dataset.py
python backend/scripts/train_model.py
uvicorn backend.app.main:app --reload
```

Then start the UI:

```bash
cd frontend
npm install
npm run dev
```

## Developer Quick Start (recommended)

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python backend/scripts/generate_dataset.py
python backend/scripts/train_model.py
uvicorn backend.app.main:app --reload
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python backend/scripts/generate_dataset.py
python backend/scripts/train_model.py
uvicorn backend.app.main:app --reload
```

## Running tests

Run unit and integration tests locally with:

```bash
.venv\Scripts\python -m pytest -q    # Windows
# or
python -m pytest -q                 # macOS / Linux
```

## CI

This repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs backend tests and builds the frontend on pushes and pull requests to `main`.

## Docker

Build and run the full stack with Docker Compose:

```bash
docker compose up --build --detach
```


## Environment Variables

- `DATABASE_URL`
- `MLFLOW_TRACKING_URI`
- `MODEL_DIR`
- `REPORTS_DIR`
- `RAW_DATA_DIR`
- `PROCESSED_DATA_DIR`
- `RISK_THRESHOLD`
- `ROOT_CAUSE_API_KEY`
- `ROOT_CAUSE_MODEL`
- `ALLOWED_ORIGINS`

## API

See [`docs/api.md`](docs/api.md).

## Architecture

See [`docs/architecture.md`](docs/architecture.md).

## Deployment

See [`docs/deployment.md`](docs/deployment.md).
