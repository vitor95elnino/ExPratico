#!/bin/bash

## Evaluate the CONSUL_MASTER_TOKEN
CMT=CONSUL_MASTER_TOKEN_${DATACENTER}${AZ_OSP16}

echo "
 export TLA=${TLA}
 export jenkins=jenkins-prd.prd.betfair
 export CHEF_ENVIRONMENT=${ENV}
 export PRODUCT=${TLA}
 export INV_PRODUCT=${TLA}
 export OS_TENANT_NAME=${TENANT}
 export TENANT=${TENANT}
 export RUNNING_USER=go
 export AVAILABILITY_ZONE=${AVAILABILITY_ZONE}
 export OSP_AZ=${AZ_OSP16}
 export ENVIRONMENT=${ENV}
 export INV_ENVIRONMENT=${ENV}
 export DC=${DATACENTER}
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
 export NETAPP_HOST=${DATACENTER}-nacosp01.inf.betfair
 export OS_USERNAME=${OS_USERNAME}
 export OS_PASSWORD=${OS_PASSWORD}
 export UDNS_SERVER=restapi.ultradns.com
 export CONSUL_MASTER_TOKEN=${!CMT}
 export UDNS_USER=api-cloudautomation" >> env_vars
 
## TODO 
if [[ ${DATACENTER} = 'ie1' ]];then
   echo " export VSD_PASSWORD=$VSD_PASSWORD_ie1" >> env_vars
else
   echo " export VSD_PASSWORD=$VSD_PASSWORD_ie2" >> env_vars
fi

if [[ ${AVAILABILITY_ZONE} = 'prd' ]];then
   echo " export SENSU_URL=http://${DATACENTER}-sensu-api-only.app.betfair" >> env_vars
   echo " export AVI_IE1=ie1-avik.inf.betfair" >> env_vars
   echo " export AVI_IE2=ie2-avik.inf.betfair" >> env_vars
else
   echo " export SENSU_URL=http://${DATACENTER}-sensu-api-only.dev.betfair" >> env_vars
   echo " export AVI_IE1=ie1-avik-qa.inf.betfair" >> env_vars
   echo " export AVI_IE2=ie2-avik-qa.inf.betfair" >> env_vars
fi

if [[ ${CLEANUP_ON} =~ "T2_NewPerimNetscalers" ]] ;then
   echo " export AVI_TIER2=true" >>env_vars
fi

if [[ ${CLEANUP_ON} =~ "T1_Netscalers" ]] ;then
   echo " export AVI_TIER1=true" >>env_vars
fi

source ./env_vars