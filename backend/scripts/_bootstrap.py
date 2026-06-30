from __future__ import annotations

import sys
from pathlib import Path


def add_project_root() -> None:
    project_root = Path(__file__).resolve().parents[2]
    root = str(project_root)
    if root not in sys.path:
        sys.path.insert(0, root)
