#!/bin/bash

# clone framework
git clone -b 1076746-osp16-decomm-tasks git@gitlab.app.betfair:devops/framework.git --depth 1
cd framework

# Build the manifest.json file
python -c "import json;print(json.dumps({'i2_${TLA}_conf_ci': {'namespace': 'i2','build': '${TLA_BRANCH}', 'repository': 'git@gitlab.app.betfair:i2/${TLA}'}, 'mon_ci_build': {'build': 'master'}, 'DevOps_CI_Build': {'build': '${inv_build_NUMBER}'}}))" >manifest.json

# At this point we are inside framework/ folder
echo "Setting the default parameters"
source ../osp16_cleanup_job_tasks/osp16_cleanup_job_set_envs.sh

## Copy script we need to use in this suite
cp roles/os_stack/library/os_stack_info.py roles/osp16_decomm/library/os_stack_info.py

source ./env_vars


docker run --rm -i \
-v ${PWD}:/workdir \
-v ${PWD%/[^/]*}/osp16_cleanup_job_tasks:/workdir/osp16_cleanup_job_tasks \
-v /home/jenkins/.ssh:/home/jenkins/.ssh:ro \
-v /home/centos/.vault_token:/home/go/.vault_token:ro \
-u jenkins \
-w /workdir \
-e WORKDIR=/workdir \
-e INFOBLOX_IP \
-e INFOBLOX_USER \
-e INFOBLOX_PASS \
-e NITRO_USER \
-e NITRO_PASS \
-e OS_USERNAME \
-e OS_PASSWORD \
-e TENANT \
-e AVI_USERNAME \
-e AVI_PASSWORD \
--env-file <(cat env_vars | tr '=' ' ' | awk '{print $2}') \
docker.app.betfair/ansible/ansible-2.8 \
  ansible-playbook pipeline.yml \
  -e stage='osp16_decomm' \
  -e dc=${DATACENTER} \
  -e availability_zone=${AVAILABILITY_ZONE} \
  -e osp_az=${OSP_AZ} \
  -e environment=${ENV} \
  -e product_environment=${ENV} \
  -e product=${TLA} \
  -e vip="True" \
  -u centos \
  --private-key=./id_rsa \
  --connection=local
