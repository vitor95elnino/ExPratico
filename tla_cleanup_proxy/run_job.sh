#!/usr/bin/env sh
pip install -r requirements.txt
#pip install .  --ignore-installed
echo "Running cleanup proxy"
python src/tla_cleanup_proxy/cleanup_proxy.py
echo "Cleanup proxy finished"