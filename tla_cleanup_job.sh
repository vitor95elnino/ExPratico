#!/bin/bash

# clone framework
git clone git@gitlab.app.betfair:devops/framework.git --depth 1
cd framework

# Fetch the latest manifest.json file for the DC
TLA=$(echo "${TLA}" | tr '[:upper:]' '[:lower:]')
DATACENTER=$(echo "${DATACENTER}" | tr '[:upper:]' '[:lower:]')
ENV=$(echo "${ENV}" | tr '[:upper:]' '[:lower:]')
artifactory_url="https://artifactory-prd.prd.betfair/artifactory"
manifest_repo="/releases"
manifest_repo_path="/${TLA}_package/${DATACENTER}/${ENV}"
latest_manifest=$(curl -sSf -u $ARTIFACTORY_USERNAME:$ARTIFACTORY_PASSWORD -H "content-type: text/plain" -X POST 'https://artifactory-prd.prd.betfair/artifactory/api/search/aql' -d 'items.find({"repo":"releases","$or":[{"path":{"$match":"'"$TLA"'_package/'"$DATACENTER"'/'"$ENV"'"}}]}).sort({"$desc": ["created"]}).limit(1)' | jq -r '.results[0].name')
#fail this job if latest_manifest is empty
if [ -z "$latest_manifest" ]; then
  echo "No manifest found for $TLA $DATACENTER $ENV"
  exit 1
fi
curl "${artifactory_url}${manifest_repo}${manifest_repo_path}/${latest_manifest}" >> manifest.json

# At this point we are inside framework/ folder
echo "Setting the default parameters"
source ../osp16_cleanup_job_tasks/osp16_cleanup_job_set_envs.sh

## Copy script we need to use in this suite
cp roles/os_stack/library/os_stack_info.py roles/osp16_decomm/library/os_stack_info.py
## Copy id_rsa to framework folder
cp ../id_rsa .
cp ../id_rsa-cert.pub .

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
  --private-key=/workdir/id_rsa \
  --connection=local

# Delete Go Pipelines
if [[ ${GOCD_Pipelines} =~ "yes" ]];then
   echo -e "Removing GOCD Pipelines for ${TLA}"

   git clone git@gitlab.app.betfair:devops/go_pipeline_builder.git --depth 1
   pushd go_pipeline_builder
   python python-modules/gpb/run_gpb.py -p ${TLA} $GO_USER $GO_PASSWORD -dp
   popd

   echo -e "Removing GOCD config for ${TLA}"
   # Get go server name from TLA gocd config. Default it to 'prd'
   GO_SERVER=$(grep -v '^\s*#' go_pipeline_builder/${TLA}.yml | grep 'go_server:' | awk '{print $2}' | tr -d "'\"")
   GO_SERVER=${GO_SERVER:-'prd'}

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