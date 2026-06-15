#!/usr/bin/env bash
# Activate the conda env and run our verification entry point (test.py),
# which in turn drives alpha-beta-CROWN over all instances in instances.csv.
# Run as root:  wsl -d Ubuntu-22.04 -u root bash <this script>
set -euo pipefail

PROJECT=/mnt/c/Users/Taewoo/alpha-beta-crown-verification

source /root/miniconda3/etc/profile.d/conda.sh
conda activate alpha-beta-crown

cd "$PROJECT"
python test.py
