#!/usr/bin/env bash
# Quick environment diagnostic for the WSL Ubuntu setup.
set -u
echo "whoami      = $(whoami)"
echo "HOME        = $HOME"
echo "uname       = $(uname -sr)"
echo "--- tools ---"
for t in git curl wget python3 pip3 conda gcc make; do
  if command -v "$t" >/dev/null 2>&1; then
    echo "$t: $(command -v "$t")"
  else
    echo "$t: MISSING"
  fi
done
echo "--- apt available (need root for installs) ---"
id -u
echo "--- disk ---"
df -h / | tail -1
