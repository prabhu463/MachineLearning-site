#!/usr/bin/env bash
set -euo pipefail

python backend/scripts/generate_dataset.py
python backend/scripts/train_model.py
