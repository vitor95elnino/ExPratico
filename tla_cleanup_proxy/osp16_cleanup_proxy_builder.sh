#!/usr/bin/env sh

echo "Running cleanup proxy"
docker run --rm  \
-v "$(pwd)":/app \
--workdir=/app \
-e JENKINS_AUT_ENDPOINT="$JENKINS_AUT_ENDPOINT" \
-e JENKINS_AUT_TOKEN="$JENKINS_AUT_TOKEN" \
-e JENKINS_PRD_ENDPOINT="$JENKINS_PRD_ENDPOINT" \
-e JENKINS_PRD_TOKEN="$JENKINS_PRD_TOKEN" \
-e JENKINS_USERNAME="$I2_JENKINS_USERNAME" \
-e TLA="$TLA" \
-e DATACENTER="$DATACENTER" \
-e ENV="$ENV" \
-e AVAILABILITY_ZONE="$AVAILABILITY_ZONE" \
-e AZ_OSP16="$AZ_OSP16" \
-e TENANT="$TENANT" \
-e GOCD_Pipelines="$GOCD_Pipelines" \
-e LOGGER_OVERRIDE="$LOGGER_OVERRIDE" \
-e JIRA_ENDPOINT="$JIRA_ENDPOINT" \
-e JIRA_USERNAME="$JIRA_USERNAME" \
-e JIRA_PASSWORD="$JIRA_PASSWORD" \
-e CHANGE_ID="$CHANGE_ID" \
docker.app.betfair/ansible/ansible-8.0 ./run_job.sh

# Check the exit code of the docker run command
if [ $? != 0 ]; then
    echo "There was a problem running the cleanup, please reach out to someone from CA."
    exit 1
fi

echo "Cleanup proxy finished"
