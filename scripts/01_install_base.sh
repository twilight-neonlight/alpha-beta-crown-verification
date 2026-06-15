#!/usr/bin/env bash
# Install Miniconda and clone alpha-beta-CROWN (with submodules) inside WSL.
# Run as root:  wsl -d Ubuntu-22.04 -u root bash <this script>
set -euo pipefail

MINICONDA_DIR=/root/miniconda3
ABCROWN_DIR=/root/alpha-beta-CROWN

# --- 1. Miniconda (no apt needed; just a downloaded installer) ---
if [ ! -x "$MINICONDA_DIR/bin/conda" ]; then
  echo "[*] Downloading Miniconda..."
  wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
  echo "[*] Installing Miniconda to $MINICONDA_DIR ..."
  bash /tmp/miniconda.sh -b -p "$MINICONDA_DIR"
  rm -f /tmp/miniconda.sh
else
  echo "[=] Miniconda already present at $MINICONDA_DIR"
fi
"$MINICONDA_DIR/bin/conda" --version

# --- 2. Clone alpha-beta-CROWN with its submodules (auto_LiRPA) ---
if [ ! -d "$ABCROWN_DIR/.git" ]; then
  echo "[*] Cloning alpha-beta-CROWN (recursive) ..."
  git clone --recursive https://github.com/Verified-Intelligence/alpha-beta-CROWN.git "$ABCROWN_DIR"
else
  echo "[=] alpha-beta-CROWN already cloned; updating submodules ..."
  git -C "$ABCROWN_DIR" submodule update --init --recursive
fi

echo "[*] Repo layout:"
ls "$ABCROWN_DIR"
echo "[*] environment file(s):"
ls "$ABCROWN_DIR"/complete_verifier/environment*.y*ml 2>/dev/null || echo "  (none in complete_verifier)"
ls "$ABCROWN_DIR"/environment*.y*ml 2>/dev/null || true
echo "[*] abcrown.py:"
ls "$ABCROWN_DIR"/complete_verifier/abcrown.py
echo "DONE"
