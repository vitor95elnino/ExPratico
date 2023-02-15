# clone framework
git clone -b 1076746-osp16-decomm-tasks git@gitlab.app.betfair:devops/framework.git --depth 1

# Fetch the latest manifest.json file for the DC
artifactory_url="https://artifactory-prd.prd.betfair/artifactory"
manifest_repo="/releases"
manifest_repo_path="/${TLA}_package/${DATACENTER}/released"
latest_manifest=$(curl -sSf -u $ARTIFACTORY_USERNAME:$ARTIFACTORY_PASSWORD -H "content-type: text/plain" -X POST 'https://artifactory-prd.prd.betfair/artifactory/api/search/aql' -d 'items.find({"repo":"releases"},{"path":"'"$TLA"'_package/'"$DATACENTER"'/released"}).sort({"$desc": ["created"]}).limit(1)' | jq -r '.results[0].name')
curl "${artifactory_url}${manifest_repo}${manifest_repo_path}/${latest_manifest}" >> manifest.json

cp id_rsa ./framework
cp id_rsa-cert.pub ./framework
cp volume_cleanup/cleanup_volumes.yml ./framework
cp manifest.json ./framework
cd ./framework

# At this point we are inside framework/ folder
echo "Setting the default parameters"
source ../osp16_cleanup_job_tasks/osp16_cleanup_job_set_envs.sh

source ./env_vars

docker run --rm -i \
-v ${PWD}:/workdir \
-v /home/jenkins/.ssh:/home/jenkins/.ssh:ro \
-v /home/centos/.vault_token:/home/go/.vault_token:ro \
-u jenkins \
-w /workdir \
-e OS_USERNAME \
-e OS_PASSWORD \
-e TENANT \
--env-file <(cat env_vars | tr '=' ' ' | awk '{print $2}') \
docker.app.betfair/ansible/ansible-2.8 \
  ansible-playbook cleanup_volumes.yml \
  -e dc=${DATACENTER} \
  -e availability_zone=${AVAILABILITY_ZONE} \
  -e osp_az=${OSP_AZ} \
  -e environment=${ENV} \
  -e product_environment=${ENV} \
  -e product=${TLA} \
  -e vms_list=${VMS_LIST} \
  -e vip="True" \
  -u centos \
  --private-key=/workdir/id_rsa \
  --connection=local
