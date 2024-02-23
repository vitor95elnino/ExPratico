#!/usr/bin/env sh
pip install -r requirements.txt

#the check if validation is required is in the python script
python src/tla_cleanup_proxy/validate_change_id_status.py
if [ $? != 0 ]; then
    exit 1
fi

#pip install .  --ignore-installed
python src/tla_cleanup_proxy/cleanup_proxy.py
# Check the exit code of the docker run command
if [ $? != 0 ]; then
    exit 1
fi
