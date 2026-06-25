from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.scripts._bootstrap import add_project_root

add_project_root()

from backend.app.db.session import Base, SessionLocal, engine
from backend.app.services.incident_service import register_model
from ml.src.data_generation import save_raw_dataset
from ml.src.training import train_models


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    dataset_path = save_raw_dataset(Path("ml/data/raw/synthetic_metrics.csv"), rows=8000)
    artifact = train_models(dataset_path)
    with SessionLocal() as db:
        register_model(
            db,
            model_name=artifact.name,
            model_version=artifact.version,
            artifact_path=str(artifact.path),
            metrics_json=str(artifact.metrics),
        )
    print(f"Trained best model: {artifact.name} -> {artifact.path}")
