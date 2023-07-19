#!/usr/bin/env sh
pip install -r requirements.txt
#pip install .  --ignore-installed
python src/tla_cleanup_proxy/cleanup_proxy.py
# Check the exit code of the docker run command
if [ $? != 0 ]; then
    exit 1
fi
