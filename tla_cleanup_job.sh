#!/bin/bash
set -x

# clone framework
git clone git@gitlab.app.betfair:devops/framework.git --depth 1
cd framework

# Fetch the latest manifest.json file for the DC
TLA=$(echo "${TLA}" | tr '[:upper:]' '[:lower:]')
DATACENTER=$(echo "${DATACENTER}" | tr '[:upper:]' '[:lower:]')
ENV=$(echo "${ENV}" | tr '[:upper:]' '[:lower:]')

# get go pipelines config from TLA repo
git archive --remote=git@gitlab.app.betfair:i2/${TLA}.git HEAD gocd/pipelines.yml| tar xvf -

# get the manifest path from gocd/pipelines.yml- if no fetch_material_from is defined, default to ENV
# if env definition was already removed from pipelines file, use * as default, will get latest manifest from artifactory
# in case env never existed, use * to get any manifest, but will fail later at 'get_prereq : render group_vars/all.yml' stage
ENV_MANIFEST_PATH=$(python3 - <<EOF
import yaml
env_name = '${ENV}'
with open('gocd/pipelines.yml', 'r') as f:
    gocd = yaml.safe_load(f)
    if gocd['environments'].get(env_name, {}).get('fetch_material_from') is not None:
        env_manifest = gocd['environments'].get(env_name, {}).get('fetch_material_from', env_name)
    elif gocd['environments'].get(env_name) is not None:
        env_manifest = env_name
    else:
        env_manifest = '*'
print(env_manifest)
EOF
)
# find latest manifest in artifactory
artifactory_url="https://artifactory-prd.prd.betfair/artifactory"
manifest_repo="releases"
manifest_relative_path="${TLA}_package/${DATACENTER}/${ENV_MANIFEST_PATH}"
echo "Searching for manifest in ${manifest_repo}/${manifest_relative_path}"
latest_manifest=$(curl -sSf -u $ARTIFACTORY_USERNAME:$ARTIFACTORY_PASSWORD -H "content-type: text/plain" -X POST "${artifactory_url}/api/search/aql" -d 'items.find({"repo":"'"${manifest_repo}"'","$or":[{"path":{"$match":"'"${manifest_relative_path}"'"}}]}).sort({"$desc": ["created"]}).limit(1)' | jq -r '.results[0]')
#fail this job if latest_manifest is null, when no manifest is found in artifactory
if [[ ("$latest_manifest" == null) || ("$latest_manifest" == "")  ]]; then
  echo "No manifest found for $TLA $DATACENTER $ENV"
  exit 1
fi

latest_manifest_path=$(echo $latest_manifest | jq -r '.path')
latest_manifest_name=$(echo $latest_manifest | jq -r '.name')
echo "Latest manifest found is ${latest_manifest_path}/${latest_manifest_name}"
curl "${artifactory_url}/${manifest_repo}/${latest_manifest_path}/${latest_manifest_name}" >> manifest.json

tier1="False"
if grep -q "TIER1_LB_CI_Build" manifest.json
then
    tier1="True"
fi

# At this point we are inside framework folder
echo "Setting the default parameters"
source ../osp16_cleanup_job_tasks/osp16_cleanup_job_set_envs.sh

## Copy script we need to use in this suite
cp roles/os_stack/library/os_stack_info.py roles/osp16_decomm/library/os_stack_info.py
## Copy id_rsa to framework folder
cp ../id_rsa .
cp ../id_rsa-cert.pub .

source ./env_vars

docker pull docker.app.betfair/ansible/ansible-8.0:latest

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
docker.app.betfair/ansible/ansible-8.0:latest \
  ansible-playbook pipeline.yml \
  -e stage='osp16_decomm' \
  -e dc=${DATACENTER} \
  -e availability_zone=${AVAILABILITY_ZONE} \
  -e oaz=${AZ_OSP16} \
  -e environment=${ENV} \
  -e product_environment=${ENV} \
  -e product=${TLA} \
  -e vip="True" \
  -e tier1=$tier1 \
  -u centos \
  -vvv \
  --private-key=/workdir/id_rsa \
  --connection=local


# Check the exit code of the docker run command
if [ $? != 0 ]; then
    echo "There was a problem running the cleanup, please check the logs."
    exit 1
fi

# Delete Go Pipelines
if [[ ${GOCD_Pipelines} =~ "yes" ]];then
   echo -e "Removing GOCD Pipelines for ${TLA}"
   # Get go server name from TLA gocd config. Default it to 'prd'
   GO_SERVER=$(grep -v '^\s*#' gocd/pipelines.yml | grep 'go_server:' | awk '{print $2}' | tr -d "'\"")
   if [[ ${GO_SERVER} == "default" || -z ${GO_SERVER} ]];then
       GO_SERVER='prd'
   fi
   # Clone the relevant repo from this group https://gitlab.app.betfair/i2/go-config-private-repos
   mkdir go_private_repo
   git clone "git@gitlab.app.betfair:i2/go-config-private-repos/${GO_SERVER}" go_private_repo

   # Delete all files for the belonging to the TLA, and push the changes.
   pushd go_private_repo
   git rm "*_${TLA}_*"
   git commit -m "Decommission ${TLA}"
   git push
   popd
fi
