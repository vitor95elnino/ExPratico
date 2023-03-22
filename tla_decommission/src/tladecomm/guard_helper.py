#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from catoolkit.library.utils.loggable import Loggable
from catoolkit.model.guard_tower.decomm.decomm_guard import DecommGuard
from catoolkit.service.cmdb.insight_manager import InsightManager
from catoolkit.service.cmdb.insight_service_arguments import InsightServiceArguments
from catoolkit.service.issue_tracker.jira.jira_manager import JiraManager
from catoolkit.service.issue_tracker.jira.jira_service_arguments import JiraServiceArguments
from catoolkit.model.guard_tower.decomm.approvers_list import ApproversList
from tladecomm.context import Context


class GuardHelper(Loggable):
    """Handles all guard rails orchestration logic"""
    # days in seconds
    DEFAULT_MAX_EXPIRATION_TIME_SECONDS = (2 * 24 * 60 * 60)
    # TODO: find a better way to allow groups
    EXTRA_APPROVERS = ApproversList
    # EXTRA_APPROVERS = [
    #     'adrian.taut@ppb.com',
    #     'ali.ansari@ppb.com',
    #     'amarjot.singh@ppb.com',
    #     'calin.rus2@ppb.com',
    #     'caolan.cooke@ppb.com',
    #     'cristian.mihali2@ppb.com',
    #     'denis.jackman@ppb.com',
    #     'federico.prando@ppb.com',
    #     'gabriel.crisan@ppb.com',
    #     'jane.stack@ppb.com',
    #     'jorge.gois@blip.pt',
    #     'jorge.oliveira@blip.pt',
    #     'jorge.torres@blip.pt',
    #     'mihaela.baciu@ppb.com',
    #     'oana.stoia@ppb.com',
    #     'philip.mather@ppb.com',
    #     'pierce.ward@ppb.com',
    #     'radu.jiga@ppb.com',
    #     'rares.titan@ppb.com',
    #     'tomas.mazak@ppb.com',
    #     'venkateswarlu.annangi@ppb.com',
    #     'yc.lam@ppb.com',
    #     'yinle.xu@ppb.com',
    # ]

    def __init__(self, context: Context):
        super().__init__()
        self._context: Context = context
        self._initialize_services()

    def _initialize_services(self) -> None:
        """Initializes services needed to guard helper"""
        # Get CMDB service
        insight_manager = InsightManager()
        if self._context.cmdb_type == insight_manager.get_type():
            self._cmdb_service = insight_manager.get_cmdb_service(
                InsightServiceArguments(
                    self._context.cmdb_endpoint,
                    self._context.cmdb_username,
                    self._context.cmdb_password
                )
            )
        else:
            raise NotImplementedError(
                f'{self._context.cmdb_type} is not supported yet'
            )

        jira_manager = JiraManager()
        if jira_manager.get_type() == self._context.issue_tracker_type:
            self._jira_service = jira_manager.create_issue_tracker_service(
                JiraServiceArguments(
                    self._context.issue_tracker_endpoint,
                    self._context.issue_tracker_username,
                    self._context.issue_tracker_password
                )
            )
        else:
            raise NotImplementedError(
                f'{self._context.issue_tracker_type} is not supported yet'
            )

    def is_this_job_allowed_to_run(self,
                                   requested_at: float = None,
                                   approved_at: float = None,
                                   approval_expiration_time: int = None
                                   ) -> bool:
        '''
        TODO: docs
        '''

        # Check if approved tla name (within url) is the same in the URL
        # These 2 entries must be equal unless someone tries to hack the
        # authorization
        if self._context.approved_tla_name is not None:
            if self._context.approved_tla_name != self._context.tla:
                raise Exception(f'Illegal attempt detected')

        decomm_guard = DecommGuard(
            self._context.tla,
            self._context.jenkins_build_user_email,
            self._cmdb_service,
            self._jira_service,
            requested_at,
            approved_at,
            approval_expiration_time,
            extra_approvers_email=self.EXTRA_APPROVERS
        )

        # set default expiration time if requested_at is set
        # otherwise one is going to ignore this checkup
        if requested_at is not None and approval_expiration_time is None:
            approval_expiration_time = self.DEFAULT_MAX_EXPIRATION_TIME_SECONDS

        return decomm_guard.validate_rules()
