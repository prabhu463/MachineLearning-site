from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.scripts._bootstrap import add_project_root

add_project_root()

from ml.src.data_generation import save_raw_dataset


if __name__ == "__main__":
    output = save_raw_dataset(Path("ml/data/raw/synthetic_metrics.csv"), rows=8000)
    print(f"Generated dataset at {output}")
