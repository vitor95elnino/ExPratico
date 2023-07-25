# -*- coding: utf-8 -*-
from os import environ
import sys

from catoolkit.library.utils.loggable import Loggable
from catoolkit.service.jenkins.jenkins_service import JenkinsService
from catoolkit.service.jenkins.decomm.osp16_tla_cleanup_job_params import TlaCleanupJobParams
from catoolkit.service.jenkins.decomm.osp16_tla_cleanup_job import TlaCleanupJob
from catoolkit.service.jenkins.osp_subnet_delete.subnet_delete_job_params import SubnetDeleteJobParams
from catoolkit.service.jenkins.osp_subnet_delete.subnet_delete_job import SubnetDeleteJob


class CleanupProxy(Loggable):
    TASK_SUCCESS_STATUS = 'SUCCESS'
    TASK_ERROR_STATUS = 'ERROR'
    TASK_SKIPPED_STATUS = 'SKIPPED'
    # jenkins results
    JENKINS_JOB_RESULT_SUCCESS = 'SUCCESS'
    JENKINS_JOB_RESULT_FAILURE = 'FAILURE'

    def __init__(self):
        super().__init__()
        self._logger.info('Starting cleanup proxy from python')
        # Jenkins
        self._jenkins_aut_endpoint = environ.get('JENKINS_AUT_ENDPOINT')
        self._jenkins_prd_endpoint = environ.get('JENKINS_PRD_ENDPOINT')
        self._jenkins_username = environ.get('JENKINS_USERNAME')
        self._jenkins_aut_token = environ.get('JENKINS_AUT_TOKEN')
        self._jenkins_prd_token = environ.get('JENKINS_PRD_TOKEN')
        self._jenkins_aut_service = self._initialize_jenkins_aut()
        self._jenkins_prd_service = self._initialize_jenkins_prd()

        # TLA params
        self.tla = environ.get('TLA')
        self.dc = environ.get('DATACENTER')
        self.env = environ.get('ENV')
        self.availability_zone = environ.get('AVAILABILITY_ZONE')
        self.az_osp16 = environ.get('AZ_OSP16')
        self.tenant = environ.get('TENANT')
        self.cloud_name = 'infra_osp16'
        self.cleanup_on = ['T1_Netscalers', 'T2_NewPerimNetscalers']
        self.isolated_repo = 'yes'
        self.nfs_volumes ='yes'
        self.subnet_delete = environ.get('SUBNET_DELETE')
        self.gocd_pipelines = environ.get('GOCD_Pipelines')
        self.tla_branch = 'master'

    def _initialize_jenkins_aut(self):
        """Initializes jenkins service"""
        jenkins_aut_service = JenkinsService(
            self._jenkins_aut_endpoint,
            self._jenkins_username,
            self._jenkins_aut_token
        )
        return jenkins_aut_service
        
    def _initialize_jenkins_prd(self):
        """Initializes jenkins service"""
        jenkins_prd_service = JenkinsService(
            self._jenkins_prd_endpoint,
            self._jenkins_username,
            self._jenkins_prd_token
        )
        return jenkins_prd_service

    def _build_tla_decomm_job_params(self) -> TlaCleanupJobParams:
        return TlaCleanupJobParams(
            dc=self.dc,
            az=self.availability_zone,
            env=self.env,
            # todo fix this tier1/ new perim
            **{
                'tla': self.tla,
                'tenant': self.tenant,
                'cloud': self.cloud_name,
                'tier1': True,
                'osp_az': self.az_osp16,
                'new_perim': True,
                'isolated_repo': self.isolated_repo,
                'gocd_pipelines': self.gocd_pipelines,
                'nfs_volumes': self.nfs_volumes,
            }
        )

    def _build_subnet_delete_job_params(self) -> SubnetDeleteJobParams:
        return SubnetDeleteJobParams(
            **{
                'dc': self.dc,
                'openstack_az': self.az_osp16,
                'tla': self.tla,
                'env': self.env,
                'tenant': self.tenant,
                'subnet_delete': self.subnet_delete
            }
        )

    def trigger_aut_cleanup(self):

        params = self._build_tla_decomm_job_params()
        self._jenkins_aut_service.trigger_jenkins_build(
            TlaCleanupJob(
                params,
            )
        )

        (build_result, build_url, full_log) = \
            self._jenkins_aut_service.poll_job_for_completion()

        self._logger.debug(full_log)
        if build_result == self.JENKINS_JOB_RESULT_FAILURE:
            self._logger.warning(
                f'Cleanup build is failure. Url is {build_url}')
            sys.exit(1)
        elif build_result == self.JENKINS_JOB_RESULT_SUCCESS:
            self._logger.info(
                f'Cleanup build is success. Url is {build_url}')
        else:
            self._logger.info(
                f'Cleanup build completed. Result is {build_result}. '
                f'Url is {build_url}')
        if build_result == self.JENKINS_JOB_RESULT_FAILURE:
            sys.exit(1)


    def trigger_subnet_cleanup(self):

        self._logger.info('Running subnet delete')

        params = self._build_subnet_delete_job_params()
        self._jenkins_prd_service.trigger_jenkins_build(
            SubnetDeleteJob(
                params,
            )
        )

        (build_result, build_url, full_log) = \
            self._jenkins_prd_service.poll_job_for_completion()

        self._logger.debug(full_log)
        if build_result == self.JENKINS_JOB_RESULT_FAILURE:
            self._logger.warning(
                f'Subnet delete build is failure. Url is {build_url}')
            sys.exit(1)
        elif build_result == self.JENKINS_JOB_RESULT_SUCCESS:
            self._logger.info(
                f'Subnet delete build is success. Url is {build_url}')
        else:
            self._logger.info(
                f'Subnet delete build completed. Result is {build_result}. '
                f'Url is {build_url}')

if __name__ == '__main__':
    CleanupProxy().trigger_aut_cleanup()
    if CleanupProxy().subnet_delete == 'true':
        CleanupProxy().trigger_subnet_cleanup()
    sys.exit(0)
