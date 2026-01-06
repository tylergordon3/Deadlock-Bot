#!/usr/bin/env bash
set -e

# Always run from repo root
cd "$(dirname "$0")"

### 🐍 HARD-BOOTSTRAP CONDA (no PATH required)
CONDA_BASE="$HOME/miniconda3"

if [ ! -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
  echo "❌ Conda not found at $CONDA_BASE"
  exit 1
fi

source "$CONDA_BASE/etc/profile.d/conda.sh"

conda activate deadlock-env || {
  echo "❌ Conda env 'deadlock-env' not found"
  conda env list
  exit 1
}

echo "🐍 Conda active: $CONDA_DEFAULT_ENV"

echo "🐍 Waking up bot..."
python main.py