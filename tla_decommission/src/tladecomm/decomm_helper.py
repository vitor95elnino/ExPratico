# -*- coding: utf-8 -*-
from os import environ
from typing import Dict
from typing import List
from typing import Optional

from catoolkit.library.osp.osp_params import Datacenter
from catoolkit.library.utils.loggable import Loggable
from catoolkit.model.decommissioning.osp10_entities import Osp10Datacenter
from catoolkit.model.decommissioning.tla_decomm import TlaDecomm
from catoolkit.service.cloud.osp10_manager import OSP10Manager
from catoolkit.service.cloud.osp10_provider import OSP10ProviderService
from catoolkit.service.cloud.osp10_provider_args import OSP10ProviderArguments
from catoolkit.service.i2.i2_config_parser import I2ConfigParser
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
        self._osp10_dcs: List[Osp10Datacenter] = []
        self._jenkins_service: Optional[JenkinsService] = None
        self.i2_config_parser: Optional[I2ConfigParser] = None
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
        self._i2_config_parser = I2ConfigParser(self.tla_name)

        # initialize git service
        self._initialize_service_scm()

        # initialize osp10 providers
        osp10_providers = self._initialize_osp10_providers()

        self._osp10_dcs = TlaDecomm.generate_osp10_servers_from_i2_config(
            self._i2_config_parser.get_environments(),
            osp10_providers
        )

        # jenkins service
        self._initialize_jenkins()

        # jenkins job
        self._decomm_job = TlaDecomm(
            tla_name=self.tla_name,
            decomm_nfs_volumes=self._context.nfs_volumes_decomm,
            tenant=self._i2_config_parser.get_tenant(),
            is_isolated_repo=self._i2_config_parser.is_isolated_repo(),
            scm_service=self._scm_service,
            osp10_deletion_assets=self._osp10_dcs,
            jenkins_service=self._jenkins_service
        )

    def _initialize_osp10_providers(self) -> Dict[str, OSP10ProviderService]:
        """Initializes and returns OSP10 Cloud Providers"""
        osp10_providers: Dict = {}
        osp10_manager = OSP10Manager()
        if self._i2_config_parser.get_cloud() == osp10_manager.get_type():
            i2_dc1_provider = osp10_manager.create_cloud_service(
                OSP10ProviderArguments(
                    username=self._context.osp10_username,
                    password=self._context.osp10_password,
                    tenant=self._i2_config_parser.get_tenant(),
                    datacenter=Datacenter.DC1
                )
            )
            osp10_providers.setdefault(Datacenter.DC1.value, i2_dc1_provider)
            i2_dc2_provider = osp10_manager.create_cloud_service(
                OSP10ProviderArguments(
                    username=self._context.osp10_username,
                    password=self._context.osp10_password,
                    tenant=self._i2_config_parser.get_tenant(),
                    datacenter=Datacenter.DC2
                )
            )
            osp10_providers.setdefault(Datacenter.DC2.value, i2_dc2_provider)
        else:
            raise NotImplementedError(
                f'{self._i2_config_parser.get_cloud()} is not supported yet'
            )
        return osp10_providers

    def _initialize_jenkins(self):
        """Initializes jenkins service"""
        self._jenkins_service = JenkinsService(
            self._context.jenkins_endpoint,
            self._context.jenkins_username,
            self._context.jenkins_password
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
