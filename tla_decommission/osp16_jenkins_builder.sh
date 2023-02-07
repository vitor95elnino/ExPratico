#!/usr/bin/env sh
BYPASS_PARTIAL_DECOMM_JOB=${BYPASS_PARTIAL_DECOMM_JOB:-'False'}

docker run --rm  \
-v "$(pwd)":/app \
--workdir=/app \
-e TLA_NAME="$TLA_NAME" \
-e NFS_VOLUMES="$NFS_VOLUMES" \
-e REQUEST_HASH="$REQUEST_HASH" \
-e APPROVAL_ENCRYPTION_KEY="$APPROVAL_ENCRYPTION_KEY" \
-e ADDITIONAL_RECIPIENTS="$ADDITIONAL_RECIPIENTS" \
-e JENKINS_AUT_ENDPOINT="$JENKINS_AUT_ENDPOINT" \
-e JENKINS_ENDPOINT="$JENKINS_ENDPOINT" \
-e JENKINS_WEBHOOK_TOKEN="$JENKINS_WEBHOOK_TOKEN" \
-e JENKINS_JOB_NAME="$JOB_NAME" \
-e JENKINS_USERNAME="$I2_JENKINS_USERNAME" \
-e JENKINS_PASSWORD="$I2_JENKINS_PASSWORD" \
-e CMDB_TYPE='jira_insight' \
-e CMDB_ENDPOINT="$JIRA_ENDPOINT" \
-e CMDB_USERNAME="$JIRA_USERNAME" \
-e CMDB_PASSWORD="$JIRA_PASSWORD" \
-e ISSUE_TRACKER_TYPE='jira' \
-e ISSUE_TRACKER_ENDPOINT="$JIRA_ENDPOINT" \
-e ISSUE_TRACKER_USERNAME="$JIRA_USERNAME" \
-e ISSUE_TRACKER_PASSWORD="$JIRA_PASSWORD" \
-e SCM_TYPE="gitlab" \
-e SCM_URL="$GITLAB_ENDPOINT" \
-e SCM_TOKEN="$GITLAB_TOKEN" \
-e OSP16_USERNAME="$OSP16_USERNAME" \
-e OSP16_PASSWORD="$OSP16_PASSWORD" \
-e BUILD_USER_ID="$BUILD_USER_ID" \
-e BUILD_USER_EMAIL="$BUILD_USER_EMAIL" \
-e LOGGER_OVERRIDE="$LOGGER_OVERRIDE" \
-e BYPASS_PARTIAL_DECOMM_JOB="$BYPASS_PARTIAL_DECOMM_JOB" \
docker.app.betfair/ansible/ansible-2.9:300 ./run_job.sh  | tee outputjob.txt
ecode=${PIPESTATUS[0]}

if (grep -e "Current issue: PPBCM" outputjob.txt); then
  STAGE="Real decom ended"
  echo STAGE=$STAGE > env_file
  echo -e "\n" >> env_file
  echo TLA_TENANT=$(grep -m 1 -e "tla_decomm - Tenant:" outputjob.txt | sed "s/.*tla_decomm - //") >> env_file
  echo -e "\n" >> env_file
  echo REQUESTER=$(grep -m 1 -e "Original request by:" outputjob.txt | sed "s/.*job - //") >> env_file
  echo -e "\n" >> env_file
  echo GUARD_PERMISSION="" >> env_file
  echo -e "\n" >> env_file
  echo GUARD_EXPIRATION="" >> env_file
  echo -e "\n" >> env_file
  echo GUARD_STATUS="" >> env_file
  echo -e "\n" >> env_file
  echo JIRA_STANDARD_CHANGE=$(grep -m 1 -e "Current issue: PPBCM" outputjob.txt | sed "s/.*issue: //") >> env_file

else
  STAGE="DRY RUN decom ended"
  echo STAGE=$STAGE > env_file
  echo -e "\n" >> env_file
  echo TLA_TENANT=$(grep -m 1 -e "tla_decomm - Tenant:" outputjob.txt | sed "s/.*tla_decomm - //") >> env_file
  echo -e "\n" >> env_file
  echo REQUESTER="" >> env_file
  echo -e "\n" >> env_file
  echo GUARD_PERMISSION=$(grep -m 1 -e "\[user_permission\]" outputjob.txt | sed "s/.*guard //") >> env_file
  echo -e "\n" >> env_file
  echo GUARD_EXPIRATION=$(grep -m 1 -e "\[expiration_date\]" outputjob.txt | sed "s/.*guard //") >> env_file
  echo -e "\n" >> env_file
  echo GUARD_STATUS=$(grep -m 1 -e "\[tla_status\]" outputjob.txt | sed "s/.*guard //") >> env_file
  echo -e "\n" >> env_file
  echo JIRA_STANDARD_CHANGE="" >> env_file

fi

echo EXIT_SCRIPT=$ecode >> env_file
