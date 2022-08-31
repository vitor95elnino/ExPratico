#!/bin/bash
if [[ ${TLA} = '' ]];then
   echo "Please enter the name of the TLA!"
   exit
fi

if [[ ${ENV} = '' ]];then
   echo "Please enter the environment!"
   exit
fi

#Get framework, sdn and inventory repo
git clone -b ${devops_build_NUMBER} git@gitlab.app.betfair:devops/framework.git --depth 1
cd framework
git clone -b ${inv_build_NUMBER} git@gitlab.app.betfair:devops/inventory.git --depth 1
git clone -b ${lb_build_NUMBER} git@gitlab.app.betfair:devops/load_balancer.git --depth 1
git clone -b ${tier1_lb_build_NUMBER} git@gitlab.app.betfair:devops/tier1_load_balancer.git --depth 1
touch manifest.json

if [[ ${ISOLATED_REPO} = 'Yes' ]];then
   git clone git@gitlab.app.betfair:i2/${TLA}.git --depth 1
   if [[ -f "${TLA}/load_balancer/netscaler/config.yml" ]]; then
      mkdir -p load_balancer/netscaler/${TLA}
      cp ${TLA}/load_balancer/netscaler/config.yml load_balancer/netscaler/${TLA}/config.yml
   fi
   if [[ -d "${TLA}/load_balancer/netscaler/domain/${TLA}" ]]; then
     mkdir -p load_balancer/netscaler/domain
     cp -r ${TLA}/load_balancer/netscaler/domain/${TLA} load_balancer/netscaler/domain/${TLA}
   fi
fi

#Set default parameters
echo "
 export jenkins=jenkins-prd.prd.betfair
 export PRODUCT=${TLA}
 export AVAILABILITY_ZONE=${AVAILABILITY_ZONE}
 export ENVIRONMENT=${ENV}
 export DC=${DATACENTER}
 export NITRO_USER=i2nsapi
 export PYTHONUNBUFFERED=true
 export INFOBLOX_IP=ns0.betfair
 export INFOBLOX_USER=svc_osp_infoblox
 export ANSIBLE_FORCE_COLOR=1
 export UDNS_SERVER=restapi.ultradns.com
 export UDNS_USER=api-cloudautomation" > env_vars


if [[ ${CLEANUP_ON} =~ "T2_OldPerimNetscalers" ]];then
   if [ ${AVAILABILITY_ZONE} = 'prd' ];then
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
fi

if [[ ${CLEANUP_ON} =~ "T1_Netscalers" ]] ;then
   if [[ ${AVAILABILITY_ZONE} = 'prd' ]];then
      echo "
        export FW_CLUSTER1=${DATACENTER}-prm-${AVAILABILITY_ZONE}fwl-01.inf.betfair,{DATACENTER}-prm-${AVAILABILITY_ZONE}fwl-02.inf.betfair
        export NS_EXTERNAL=${DATACENTER}extprd101.inf.betfair,${DATACENTER}extprd102.inf.betfair
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

source ./env_vars

echo -e "Removing netscaler records for ${TLA}"

if [[ ${CLEANUP_ON} =~ "T2_OldPerimNetscalers" ]];then
   ansible-playbook playbooks/cleanup_netscalers.yml -i inventory/${TLA}/inventory \
   -e "\
   dc=${DATACENTER} \
   availability_zone=${AVAILABILITY_ZONE} \
   environment=${ENV} \
   product_environment=${ENV} \
   product=${TLA} \
   tier2ns=true \
   manifest=manifest.json" -vvv;
fi

if [[ ${CLEANUP_ON} =~ "T2_NewPerimNetscalers" ]];then
   echo "Running cleanup on New Perimeter Netscalers..."
   ansible-playbook playbooks/cleanup_netscalers.yml -i inventory/${TLA}/inventory \
   -e "\
   dc=${DATACENTER} \
   availability_zone=${AVAILABILITY_ZONE} \
   manifest=manifest.json \
   environment=${ENV} \
   product_environment=${ENV} \
   new_perim=true \
   product=${TLA}" -vvv;
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
