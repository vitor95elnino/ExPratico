FROM docker.app.betfair/ansible/ansible-8.0:latest

COPY tla_decommission /tmp/tla_decommission

RUN pip install -r /tmp/tla_decommission/requirements.txt && \
    pip install /tmp/tla_decommission --ignore-installed
