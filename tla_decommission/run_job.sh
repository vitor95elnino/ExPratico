#!/usr/bin/env sh
pip install -r requirements.txt
pip install .  --ignore-installed
python bin/jenkins_tla_decommission
