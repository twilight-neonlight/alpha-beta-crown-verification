#!/usr/bin/env bash
# Create the alpha-beta-CROWN conda environment from the project's pinned export
# (PyTorch 2.5.1). Run as root:
#   wsl -d Ubuntu-22.04 -u root bash <this script>
set -euo pipefail

CONDA=/root/miniconda3/bin/conda
ENV_NAME=alpha-beta-crown
ENV_FILE=/root/alpha-beta-CROWN/complete_verifier/environment_pyt251.yaml

source /root/miniconda3/etc/profile.d/conda.sh

# Newer conda requires explicitly accepting the Anaconda channel Terms of Service.
echo "[*] Accepting Anaconda channel Terms of Service ..."
"$CONDA" tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main || true
"$CONDA" tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r || true

if "$CONDA" env list | grep -q "^${ENV_NAME} "; then
  echo "[=] conda env '$ENV_NAME' already exists."
else
  echo "[*] Creating conda env '$ENV_NAME' from $ENV_FILE ..."
  "$CONDA" env create -n "$ENV_NAME" -f "$ENV_FILE"
fi

conda activate "$ENV_NAME"

# auto_LiRPA is a git submodule, not part of the conda export. Install it editable
# WITHOUT deps so it doesn't try to pull a conflicting torch version.
echo "[*] Installing auto_LiRPA (editable, no-deps) ..."
pip install --no-deps -e /root/alpha-beta-CROWN/auto_LiRPA

echo "[*] Verifying imports ..."
python - <<'PY'
import torch, onnx, onnxruntime
print("torch       :", torch.__version__, "| cuda available:", torch.cuda.is_available())
print("onnx        :", onnx.__version__)
print("onnxruntime :", onnxruntime.__version__)
import auto_LiRPA
print("auto_LiRPA  : OK")
import onnx2pytorch
print("onnx2pytorch: OK")
PY
echo "DONE"
