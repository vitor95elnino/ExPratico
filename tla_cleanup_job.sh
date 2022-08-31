#!/bin/bash

export TLA=${TLA,,}

if [[ ${TLA} = '' ]]; then
   echo "Please enter the name of the TLA!"
   exit
fi

if [[ ${ENV} = '' ]]; then
   echo "Please enter the environment!"
   exit
fi

# set default TLA branch name to keep backward compatibility (#911204)
TLA_BRANCH=${TLA_BRANCH:-'master'}

# Get framework, sdn and inventory repo
git clone -b ${devops_build_NUMBER} git@gitlab.app.betfair:devops/framework.git --depth 1
cd framework
git clone -b ${sdn_build_NUMBER} git@gitlab.app.betfair:devops/sdn.git --depth 1
git clone -b ${inv_build_NUMBER} git@gitlab.app.betfair:devops/inventory.git --depth 1
git clone -b ${lb_build_NUMBER} git@gitlab.app.betfair:devops/load_balancer.git --depth 1
git clone -b ${tier1_lb_build_NUMBER} git@gitlab.app.betfair:devops/tier1_load_balancer.git --depth 1
git clone git@gitlab.app.betfair:devops/go_pipeline_builder.git --depth 1
git clone git@gitlab.app.betfair:devops/monitoring.git

if [[ ${ISOLATED_REPO} = 'Yes' ]];then
   echo "Cloning ${TLA_BRANCH} branch from ${TLA} repo..."
   git clone -b ${TLA_BRANCH} git@gitlab.app.betfair:i2/${TLA}.git --depth 1
   if [[ -f "${TLA}/load_balancer/avi/config.yml" ]]; then
      mkdir -p load_balancer/avi/${TLA}
      cp ${TLA}/load_balancer/avi/config.yml load_balancer/avi/${TLA}/config.yml
   fi
   if [[ -f "${TLA}/load_balancer/netscaler/config.yml" ]]; then
      mkdir -p load_balancer/netscaler/${TLA}
      cp ${TLA}/load_balancer/netscaler/config.yml load_balancer/netscaler/${TLA}/config.yml
   fi
   if [[ -d "${TLA}/load_balancer/netscaler/domain/${TLA}" ]]; then
     mkdir -p load_balancer/netscaler/domain
     cp -r ${TLA}/load_balancer/netscaler/domain/${TLA} load_balancer/netscaler/domain/${TLA}
   fi
   if [[ -d "${TLA}/inventory" ]]; then
     mkdir -p inventory/${TLA}
     rm -rf inventory/${TLA}/*
     cp -r ${TLA}/inventory/ inventory/${TLA}
   fi
   if [[ -f "${TLA}/gocd/pipelines.yml" ]]; then
      cp -r ${TLA}/gocd/pipelines.yml go_pipeline_builder/${TLA}.yml
   fi
   if [[ -d "${TLA}/sdn" ]]; then
      mkdir -p sdn/nuage
      cp -r ${TLA}/sdn sdn/nuage/${TLA}
   fi
fi

python -c "import json;print json.dumps({'i2_${TLA}_conf_ci': {'build': 'master'}, 'SDN_CI_Build': {'build': '${sdn_build_NUMBER}'}, 'inv_ci_build': {'build': '${inv_build_NUMBER}'}, 'LB_CI_Build': {'build': '${lb_build_NUMBER}'}})" > manifest.json

# Set default parameters
echo "
 export jenkins=jenkins-prd.prd.betfair
 export CHEF_ENVIRONMENT=${ENV}
 export PRODUCT=${TLA}
 export INV_PRODUCT=${TLA}
 export OS_TENANT_NAME=\"${TENANT}\"
 export TENANT=\"${TENANT}\"
 export RUNNING_USER=go
 export AVAILABILITY_ZONE=${AVAILABILITY_ZONE}
 export ENVIRONMENT=${ENV}
 export INV_ENVIRONMENT=${ENV}
 export DC=${DATACENTER}
 export OS_AUTH_URL=https://${DATACENTER}-osp10-inf.inf.betfair:5000/v3/
 export OS_NAME=${DATACENTER}-osp10-inf
 export OS_USER_DOMAIN_NAME=osp-ldap
 export OS_PROJECT_DOMAIN_NAME=osp-ldap
 export OS_IDENTITY_API_VERSION=3
 export VSD_API_VERSION=3.0
 export VSD_API_URL=https://${DATACENTER}-nuvsd01-inf.inf.betfair:8443
 export VSD_API_URL_ie1=https://ie1-nuvsd01-inf.inf.betfair:8443
 export VSD_API_URL_ie2=https://ie2-nuvsd01-inf.inf.betfair:8443
 export VSD_USERNAME=csproot
 export VSD_ENTERPRISE=csp
 export VAULT_ADDR=https://vault-prd.prd.betfair
 export INFOBLOX_IP=ns0.betfair
 export INFOBLOX_USER=svc_osp_infoblox
 export NITRO_USER=i2nsapi
 export ARTIFACTORY_URL=https://artifactory-prd.prd.betfair/artifactory/
 export ARTIFACTORY_USERNAME=admin
 export PYTHONUNBUFFERED=true
 export ANSIBLE_FORCE_COLOR=1
 export AVI_USERNAME=admin
 export NETAPP_HOST=${DATACENTER}-nacosp01.inf.betfair
 export UDNS_SERVER=restapi.ultradns.com
 export UDNS_USER=api-cloudautomation" > env_vars

if [[ ${DATACENTER} = 'ie1' ]];then
   echo "
      export VSD_PASSWORD=$VSD_PASSWORD_ie1 " >> env_vars
else
   echo "
      export VSD_PASSWORD=$VSD_PASSWORD_ie2 " >> env_vars
fi

if [[ ${AVAILABILITY_ZONE} = 'prd' ]];then
   echo "
      export SENSU_URL=http://${DATACENTER}-sensu-api-only.app.betfair
      export AVI_IE1=ie1-avik.inf.betfair
      export AVI_IE2=ie2-avik.inf.betfair " >> env_vars
else
   echo "
      export SENSU_URL=http://${DATACENTER}-sensu-api-only.dev.betfair
      export AVI_IE1=ie1-avik-qa.inf.betfair
      export AVI_IE2=ie2-avik-qa.inf.betfair " >> env_vars
fi

if [[ ${CLEANUP_ON} =~ "T1_Netscalers" ]] ;then
   if [[ ${AVAILABILITY_ZONE} = 'prd' ]];then
      echo "
        export FW_CLUSTER1=${DATACENTER}-prm-${AVAILABILITY_ZONE}fwl-01.inf.betfair,{DATACENTER}-prm-${AVAILABILITY_ZONE}fwl-02.inf.betfair
        export NS_EXTERNAL=${DATACENTER}extprd101.inf.betfair,${DATACENTER}extprd102.inf.betfair,${DATACENTER}extprd103.inf.betfair
        export FW_CLUSTER2=${DATACENTER}-prm-${AVAILABILITY_ZONE}fwl-03.inf.betfair,{DATACENTER}-prm-${AVAILABILITY_ZONE}fwl-04.inf.betfair " >>env_vars
   else
      if [[ ${CLEANUP_ON} =~ "T2_OldPerimNetscalers" ]];then
         echo "
            export NS_EXTERNAL=${DATACENTER}extpflb101.inf.betfair " >> env_vars
      else
         echo "
           export NS_EXTERNAL=${DATACENTER}-dev-tr1lbr-01.inf.betfair
           export FW_CLUSTER1=${DATACENTER}-prm-devfwl-01.inf.betfair " >>env_vars
      fi
   fi
fi

if [[ ${CLEANUP_ON} =~ "T2_OldPerimNetscalers" || ${CLEANUP_ON} =~ "T2_NewPerimNetscalers" ]] ;then
   echo "
     export AVI_TIER2=true " >>env_vars
fi

if [[ ${CLEANUP_ON} =~ "T1_Netscalers" ]] ;then
   echo "
     export AVI_TIER1=true " >>env_vars
fi

source ./env_vars

echo -e "Removing AVI records for ${TLA}"

   ansible-playbook playbooks/cleanup_avi.yml -i "127.0.0.1," \
   -e "\
   dc=${DATACENTER} \
   availability_zone=${AVAILABILITY_ZONE} \
   environment=${ENV} \
   product_environment=${ENV} \
   product=${TLA} \
   avi_ie1=${AVI_IE1} \
   avi_ie2=${AVI_IE2} \
   avi_tier2=${AVI_TIER2} \
   avi_tier1=${AVI_TIER1} \
   manifest=manifest.json" -vv;

echo -e "Removing netscaler records for ${TLA}"

if [[ ${CLEANUP_ON} =~ "T2_OldPerimNetscalers" ]];then
   if [[ ${AVAILABILITY_ZONE} = 'prd' ]];then
      echo "
        export NS_CLUSTER1=${DATACENTER}vpx${AVAILABILITY_ZONE}101.inf.betfair,${DATACENTER}vpx${AVAILABILITY_ZONE}201.inf.betfair
        export NS_CLUSTER2=${DATACENTER}vpx${AVAILABILITY_ZONE}102.inf.betfair,${DATACENTER}vpx${AVAILABILITY_ZONE}202.inf.betfair
        export NS_SITE1=${DATACENTER}vpxpdlb101-201
        export NS_SITE2=${DATACENTER}vpxpdlb102-202 " >>env_vars
   else
      echo "
        export NS_CLUSTER1=${DATACENTER}vpx${AVAILABILITY_ZONE}101.inf.betfair,${DATACENTER}vpx${AVAILABILITY_ZONE}102.inf.betfair
        export NS_CLUSTER2=${DATACENTER}vpx${AVAILABILITY_ZONE}201.inf.betfair,${DATACENTER}vpx${AVAILABILITY_ZONE}202.inf.betfair
        export NS_SITE1=${DATACENTER}VPX${AVAILABILITY_ZONE}101-2
        export NS_SITE2=${DATACENTER}VPX${AVAILABILITY_ZONE}201-2 " >>env_vars
   fi

   source ./env_vars

   docker run --rm -i \
     -v ${PWD}:/workdir \
     -v /home/jenkins/.ssh:/home/jenkins/.ssh:ro \
     -v /home/centos/.vault_token:/home/go/.vault_token:ro \
     -u jenkins -w /workdir \
     -e WORKDIR=/workdir \
     -e INFOBLOX_PASS \
     -e NITRO_PASS \
     --env-file <(cat env_vars | tr '=' ' ' | awk '{print $2}') \
     docker.app.betfair/ansible/ansible-2.8 \
       ansible-playbook playbooks/cleanup_netscalers.yml -i inventory/${TLA}/inventory \
       -e dc=${DATACENTER} \
       -e availability_zone=${AVAILABILITY_ZONE} \
       -e environment=${ENV} \
       -e product_environment=${ENV} \
       -e product=${TLA} \
       -e tier2ns=true \
       -e manifest=manifest.json -vvv;
fi

if [[ ${CLEANUP_ON} =~ "T2_NewPerimNetscalers" ]];then

   if [[ ${AVAILABILITY_ZONE} = 'prd' ]];then
      echo "
        export NS_CLUSTERS='${DATACENTER}-prm-tr2lbr-01.inf.betfair;${DATACENTER}-prm-tr2lbr-02.inf.betfair;${DATACENTER}-prm-tr2lbr-03.inf.betfair;${DATACENTER}-prm-tr2lbr-04.inf.betfair'
        export NS_PROTO=http " >>env_vars
   else
      echo "
        export NS_CLUSTER1=${DATACENTER}-${AVAILABILITY_ZONE}-tr2lbr-01.inf.betfair
        export NS_CLUSTER2=${DATACENTER}-${AVAILABILITY_ZONE}-tr2lbr-02.inf.betfair " >>env_vars
   fi

   source ./env_vars

   docker run --rm -i \
   -v ${PWD}:/workdir \
   -v /home/jenkins/.ssh:/home/jenkins/.ssh:ro \
   -v /home/centos/.vault_token:/home/go/.vault_token:ro \
   -u jenkins -w /workdir \
   -e WORKDIR=/workdir \
   -e INFOBLOX_PASS \
   -e NITRO_PASS \
   --env-file <(cat env_vars | tr '=' ' ' | awk '{print $2}') \
   docker.app.betfair/ansible/ansible-2.8 \
     ansible-playbook playbooks/cleanup_netscalers.yml -i inventory/${TLA}/inventory \
     -e dc=${DATACENTER} \
     -e availability_zone=${AVAILABILITY_ZONE} \
     -e manifest=manifest.json \
     -e environment=${ENV} \
     -e product_environment=${ENV} \
     -e new_perim=true \
     -e product=${TLA} -vvv;
fi

if [[ ${CLEANUP_ON} =~ "T1_Netscalers" ]];then
   source ./env_vars

   echo "Running cleanup on UltraDNS"
   docker run --rm -i \
   -v ${PWD}:/workdir \
   -v /home/jenkins/.ssh:/home/jenkins/.ssh:ro \
   -v /home/centos/.vault_token:/home/go/.vault_token:ro \
   -u jenkins -w /workdir \
   -e WORKDIR=/workdir \
   -e INFOBLOX_PASS \
   -e UDNS_PASS \
   --env-file <(cat env_vars | tr '=' ' ' | awk '{print $2}') \
   docker.app.betfair/ansible/ansible-2.8 \
     ansible-playbook playbooks/cleanup_ultradns.yml \
     -e dc=${DATACENTER} \
     -e availability_zone=${AVAILABILITY_ZONE} \
     -e environment=${ENV} \
     -e product_environment=${ENV} \
     -e product=${TLA}

   echo "Running cleanup on SRX firewalls"
   docker run --rm -i \
     -v ${PWD}:/workdir \
     -v /home/jenkins/.ssh:/home/jenkins/.ssh:ro \
     -u jenkins -w /workdir \
     -e WORKDIR=/workdir \
     -e INFOBLOX_PASS \
     -e NITRO_PASS \
     --env-file <(cat env_vars | tr '=' ' ' | awk '{print $2}') \
     docker.app.betfair/ansible/ansible-2.8 \
     ansible-playbook playbooks/delete_srx_external.yml \
       -i inventories/tier1_srx \
       -l "${DATACENTER}_${ENV}" \
       -e dc=${DATACENTER} \
       -e availability_zone=${AVAILABILITY_ZONE} \
       -e environment=${ENV} \
       -e product_environment=${ENV} \
       -e product=${TLA}

   # Zip up the SRX log files for archiving
   pushd playbooks
   zip -r srx_decomm_logs.zip deploy_*.log
   mv srx_decomm_logs.zip ../../
   popd

   echo "Running cleanup on Tier1 Netscalers..."
   docker run --rm -i \
   -v ${PWD}:/workdir \
   -v /home/jenkins/.ssh:/home/jenkins/.ssh:ro \
   -v /home/centos/.vault_token:/home/go/.vault_token:ro \
   -u jenkins -w /workdir \
   -e WORKDIR=/workdir \
   -e INFOBLOX_PASS \
   -e NITRO_PASS \
   --env-file <(cat env_vars | tr '=' ' ' | awk '{print $2}') \
   docker.app.betfair/ansible/ansible-2.8 \
     ansible-playbook playbooks/cleanup_netscalers.yml -i inventory/${TLA}/inventory \
     -e dc=${DATACENTER} \
     -e availability_zone=${AVAILABILITY_ZONE} \
     -e manifest=manifest.json \
     -e environment=${ENV} \
     -e product_environment=${ENV} \
     -e tier1ns=true \
     -e product=${TLA}
fi

if [[ ${OSP_CLEANUP} =~ "yes" ]];then
    echo -e "Removing Nuage and Openstack records for ${TLA}"
    #This step has to be the last one since we have TLAs with multiple ENVs in one AZ.
    #The job will fail until the last ENV will be cleaned up since the Nuage TLA Zone can not be deleted while the ENVs are sharing the same Zone.

    docker pull docker.app.betfair/ansible/ansible-2.8 > /dev/null
    docker run --rm -i -v ${PWD}:/workdir -v /home/jenkins/.ssh:/home/jenkins/.ssh:ro -v /home/centos/.vault_token:/home/go/.vault_token:ro -u jenkins -w /workdir \
       -e WORKDIR=/workdir -e VAULT_ADDR -e OS_NAME -e OS_TENANT_NAME -e OS_USERNAME -e OS_PASSWORD -e OS_IDENTITY_API_VERSION -e INFOBLOX_IP -e INFOBLOX_USER -e INFOBLOX_PASS -e VSD_API_VERSION -e VSD_API_URL -e VSD_ENTERPRISE -e VSD_USERNAME -e VSD_PASSWORD -e SENSU_URL -e PYTHONUNBUFFERED -e ANSIBLE_FORCE_COLOR -e INV_PRODUCT -e INV_ENVIRONMENT \
       docker.app.betfair/ansible/ansible-2.8 \
       ansible-playbook playbooks/cleanup_environment.yml -i plugins/inventories/openstack.py -e dc=${DATACENTER} -e availability_zone=${AVAILABILITY_ZONE} -e product_environment=${ENV} -e product=${TLA} -e cloud=${OS_NAME} -e tenant=${TENANT} -e manifest=manifest.json -vv


    if [[ ${NFS_VOLUMES} =~ "yes" ]];then
      echo "Starting NFS decommissioning activities on ${TLA}"
      docker run --rm -i \
         -v ${PWD}:/workdir \
         -v /home/jenkins/.ssh:/home/jenkins/.ssh:ro \
         -v /home/centos/.vault_token:/home/go/.vault_token:ro \
         -u jenkins -w /workdir \
         -e WORKDIR=/workdir \
         -e NFS_USER \
         -e NFS_PASSWORD \
         --env-file <(cat env_vars | tr '=' ' ' | awk '{print $2}') \
         docker.app.betfair/ansible/ansible-2.8 \
         ansible-playbook playbooks/cleanup_nfs_oslg.yml \
            -e dc=${DATACENTER} \
            -e availability_zone=${AVAILABILITY_ZONE} \
            -e environment=${ENV} \
            -e product_environment=${ENV} \
            -e product=${TLA}

      set +e
      echo "Cleaning up the NFS volume mounting points in the configuration file monitoring/rsyslog-server/oslg/${DATACENTER}/${AVAILABILITY_ZONE}.yml"
      docker pull docker.app.betfair/cloudautomation/python-git > /dev/null
      docker run --rm -i \
         -v ${PWD}/..:/workdir \
         -v /home/jenkins/.ssh:/home/jenkins/.ssh:ro \
         -v /home/jenkins/.gitconfig:/home/jenkins/.gitconfig:ro \
         -u jenkins \
         -w /workdir/framework/monitoring \
         -e WORKDIR=/workdir \
         -e GITLAB_TOKEN \
         --env-file <(cat env_vars | tr '=' ' ' | awk '{print $2}') \
         docker.app.betfair/cloudautomation/python-git \
         python3 /workdir/nfs_volumemount_cleaner.py ${TLA} ${AVAILABILITY_ZONE} ${DATACENTER} '.'
      mount_result=$?

      if [ $mount_result -ne 0 ]; then
         echo "ERROR: Failed to process python script nfs_volumemount_cleaner.py to decommission the TLA in NFS mountpoint configuration file."
      fi
    else
      echo "Skipping NFS decommissioning activities on ${TLA}"
    fi
fi

if [[ ${GOCD_Pipelines} =~ "yes" ]];then
   echo -e "Removing GOCD Pipelines for ${TLA}"

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
