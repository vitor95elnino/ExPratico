# -*- coding: utf-8 -*-
from os import environ
from typing import Dict
from typing import List
from typing import Optional

from catoolkit.library.osp.osp_params import Datacenter
from catoolkit.library.osp.osp16_params import AvailabilityZone
from catoolkit.library.utils.loggable import Loggable
from catoolkit.model.decommissioning.osp16_entities import Osp16Datacenter
from catoolkit.model.decommissioning.osp16_entities import Osp16AvailabilityZone
from catoolkit.model.decommissioning.tla_decomm_16 import TlaDecomm
from catoolkit.service.cloud.osp16_manager import OSP16Manager
from catoolkit.service.cloud.osp16_provider import OSP16ProviderService
from catoolkit.service.cloud.osp16_provider_args import OSP16ProviderArguments
from catoolkit.service.i2.i2_osp16_config_parser import I2ConfigParser
from catoolkit.service.jenkins.jenkins_service import JenkinsService
from catoolkit.service.scm.gitlab_manager import GitlabManager
from catoolkit.service.scm.gitlab_service_arguments import GitlabServiceArguments
from catoolkit.service.scm.scm_interface import ScmServiceInterface
from tladecomm.context import Context


class DecommHelper(Loggable):
    """Handles all decommission orchestration logic"""

    FLAG_IGNORE_HTTPS_ERRORS = 'PYTHONHTTPSVERIFY'

    def __init__(self, context: Context):
        super().__init__()
        self._context: Context = context
        self._decomm_job: Optional[TlaDecomm] = None
        self._scm_service: Optional[ScmServiceInterface] = None
        self._osp16_dcs: List[Osp16Datacenter] = []
        self._jenkins_service: Optional[JenkinsService] = None
        self._jenkins_aut_service: Optional[JenkinsService] = None
        self._i2_osp16_config_parser: Optional[I2ConfigParser] = None
        self._initialize_services()
        self._ssl_verify = False if '0' == environ.get(
            self.FLAG_IGNORE_HTTPS_ERRORS,
            True) else True
        self._logger.debug(
            f'ssl_verify = {self._ssl_verify}')

    def _initialize_services(self):
        """Initializes all required services"""
        # find and set tla_name
        if self._context.is_dry_run():
            self.tla_name = self._context.tla
        else:
            self.tla_name = self._context.approved_tla_name

        # service to retrieve tla details
        self._i2_osp16_config_parser = I2ConfigParser(self.tla_name)

        # initialize git service
        self._initialize_service_scm()

        # initialize osp16 providers
        self.osp16_providers = self._initialize_osp16_providers()

        # todo adapt this to osp16
        self._osp16_dcs = TlaDecomm.generate_osp16_servers_from_i2_config(
            self._i2_osp16_config_parser.get_environments(),
            self.osp16_providers
        )

        # jenkins service
        self._initialize_jenkins()
        self._initialize_jenkins_aut()

        # jenkins job
        self._decomm_job = TlaDecomm(
            tla_name=self.tla_name,
            decomm_nfs_volumes=self._context.nfs_volumes_decomm,
            tenant=self._i2_osp16_config_parser.get_tenant(),
            is_isolated_repo=self._i2_osp16_config_parser.is_isolated_repo(),
            scm_service=self._scm_service,
            osp16_deletion_assets=self._osp16_dcs,
            jenkins_service=self._jenkins_service,
            jenkins_aut_service=self._jenkins_aut_service

        )

    def _initialize_osp16_providers(self) -> Dict[str, OSP16ProviderService]:
        """Initializes and returns OSP16 Cloud Providers"""
        osp16_providers: Dict = {}
        osp16_manager = OSP16Manager()
        if self._i2_osp16_config_parser.get_cloud() == osp16_manager.get_type():
            i1_dc1_dev_provider = osp16_manager.create_cloud_service(
                OSP16ProviderArguments(
                    username=self._context.osp16_username,
                    password=self._context.osp16_password,
                    tenant=self._i2_osp16_config_parser.get_tenant(),
                    datacenter=Datacenter.DC1,
                    az=AvailabilityZone.DEV
                )
            )
            osp16_providers.setdefault(str(Datacenter.DC1.value + AvailabilityZone.DEV.value), i1_dc1_dev_provider)
            i2_dc1_dev_provider = osp16_manager.create_cloud_service(
                OSP16ProviderArguments(
                    username=self._context.osp16_username,
                    password=self._context.osp16_password,
                    tenant=self._i2_osp16_config_parser.get_tenant(),
                    datacenter=Datacenter.DC2,
                    az=AvailabilityZone.DEV
                )
            )
            osp16_providers.setdefault(str(Datacenter.DC2.value + AvailabilityZone.DEV.value), i2_dc1_dev_provider)
            i1_dc1_prd_provider = osp16_manager.create_cloud_service(
                OSP16ProviderArguments(
                    username=self._context.osp16_username,
                    password=self._context.osp16_password,
                    tenant=self._i2_osp16_config_parser.get_tenant(),
                    datacenter=Datacenter.DC1,
                    az=AvailabilityZone.PRD
                )
            )
            osp16_providers.setdefault(str(Datacenter.DC1.value + AvailabilityZone.PRD.value), i1_dc1_prd_provider)
            i1_dc2_prd_provider = osp16_manager.create_cloud_service(
                OSP16ProviderArguments(
                    username=self._context.osp16_username,
                    password=self._context.osp16_password,
                    tenant=self._i2_osp16_config_parser.get_tenant(),
                    datacenter=Datacenter.DC2,
                    az=AvailabilityZone.PRD
                )
            )
            osp16_providers.setdefault(str(Datacenter.DC2.value + AvailabilityZone.PRD.value), i1_dc2_prd_provider)
        else:
            raise NotImplementedError(
                f'{self._i2_osp16_config_parser.get_cloud()} is not supported yet'
            )
        return osp16_providers

    def _initialize_jenkins(self):
        """Initializes jenkins service"""
        self._jenkins_service = JenkinsService(
            self._context.jenkins_endpoint,
            self._context.jenkins_username,
            self._context.jenkins_token
        )
    def _initialize_jenkins_aut(self):
        """Initializes jenkins service"""
        self._jenkins_aut_service = JenkinsService(
            self._context.jenkins_aut_endpoint,
            self._context.jenkins_username,
            self._context.jenkins_aut_token
        )

    def _initialize_service_scm(self):
        """Get/Create SCM service"""
        gitlab_manager = GitlabManager()
        if gitlab_manager.get_type() == self._context.scm_type:
            self._scm_service = gitlab_manager.create_git_service(
                GitlabServiceArguments(
                    self._context.scm_url,
                    self._context.scm_token
                )
            )
        else:
            # TODO: add support for github
            raise NotImplementedError(
                f'{self._context.scm_type} is not supported yet'
            )

    def dry_run(self):
        """Print assets to be decommissioned"""
        # TODO: reuse the same logger
        return self._decomm_job.dry_run()

    def run(self):
        """Run the decomm"""
        # TODO: reuse the same logger
        return self._decomm_job.run()

    @property
    def osp_services(self):
        return self.osp16_providers
