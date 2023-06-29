#!/usr/bin/env sh

docker run --rm  \
-v "$(pwd)":/app \
--workdir=/app \
-e JENKINS_AUT_ENDPOINT="$JENKINS_AUT_ENDPOINT" \
-e JENKINS_AUT_TOKEN="$JENKINS_AUT_TOKEN" \
-e JENKINS_USERNAME="$I2_JENKINS_USERNAME" \
-e TLA="$TLA" \
-e DATACENTER="$DATACENTER" \
-e ENV="$ENV" \
-e AVAILABILITY_ZONE="$AVAILABILITY_ZONE" \
-e AZ_OSP16="$AZ_OSP16" \
-e TENANT="$TENANT" \
-e CLOUD_NAME="$CLOUD_NAME" \
-e CLEANUP_ON="$CLEANUP_ON" \
-e ISOLATED_REPO="$ISOLATED_REPO" \
-e NFS_VOLUMES="$NFS_VOLUMES" \
-e GOCD_Pipelines="$GOCD_Pipelines" \
-e TLA_BRANCH="$TLA_BRANCH" \
-e LOGGER_OVERRIDE="$LOGGER_OVERRIDE" \
docker.app.betfair/ansible/ansible-2.9:300 ./run_job.sh  | tee outputjob.txt
ecode=${PIPESTATUS[0]}
