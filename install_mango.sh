#!/usr/bin/env bash
set -euo pipefail

# Create the MANGO environment and install the package.
CONDA_BASE=$(conda info --base 2>/dev/null) || { echo "Error: conda is not installed or cannot be initialised."; exit 1; }
conda env create -f environment.yaml || conda env update -f environment.yaml
source "${CONDA_BASE}/bin/activate" mango

# Trained weights. Set WEIGHTS_URL once the weights are published.
WEIGHTS_DIR="mango/trained_models/"
WEIGHTS_URL=""
if [ -n "$WEIGHTS_URL" ]; then
    mkdir -p "$WEIGHTS_DIR"
    wget -O "$WEIGHTS_DIR/MANGO.zip" "$WEIGHTS_URL"
    unzip -o "$WEIGHTS_DIR/MANGO.zip" -d "$WEIGHTS_DIR"
    rm "$WEIGHTS_DIR/MANGO.zip"
fi

pip install -e .
echo "Installed MANGO. PyRosetta (PyRosetta_PRE embeddings only) must be installed separately."
