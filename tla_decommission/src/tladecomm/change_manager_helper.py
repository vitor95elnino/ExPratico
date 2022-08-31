# -*- coding: utf-8 -*-
from catoolkit.library.utils.loggable import Loggable
from catoolkit.model.change_management.change_decomm import ChangeDecomm
from catoolkit.service.cmdb.insight_manager import InsightManager
from catoolkit.service.cmdb.insight_service_arguments import InsightServiceArguments
from catoolkit.service.issue_tracker.jira.jira_manager import JiraManager
from catoolkit.service.issue_tracker.jira.jira_service_arguments import JiraServiceArguments
from catoolkit.service.scm.gitlab_manager import GitlabManager
from catoolkit.service.scm.gitlab_service_arguments import GitlabServiceArguments
from tladecomm.context import Context


class ChangeManagerHelper(Loggable):
    """Handles all Change Management logic in the Decomm Job"""

    SCM_STATUS_TRACKER_REPO = 'cloud-automation/tla_decommission_scripts'
    SCM_STATUS_TRACKER_PATH = 'tla_decommission/var/history/'
    SCM_STATUS_TRACKER_BRANCH_BASE = 'master'

    def __init__(self, context: Context):
        super().__init__()
        self._context: Context = context
        self._decomm_cm: ChangeDecomm = None
        self._initialize_cm_model()

    def _initialize_cm_model(self) -> None:
        """ Initializes the change management model

        It creates the model object with required paramenters
        """
        if not self._decomm_cm:
            # Get/Create CMDB service
            insight_manager = InsightManager()
            if insight_manager.get_type() == self._context.cmdb_type:
                cmdb_service = insight_manager.get_cmdb_service(
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

            # Get / Create issue tracker service
            jira_manager = JiraManager()
            if jira_manager.get_type() == self._context.issue_tracker_type:
                issue_tracker_service = jira_manager.create_issue_tracker_service(
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

            # Get/Create SCM service
            gitlab_manager = GitlabManager()
            if gitlab_manager.get_type() == self._context.scm_type:
                scm_service = gitlab_manager.create_git_service(
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

            # create Decom model (biz logic)
            self._decomm_cm = ChangeDecomm(
                issue_tracker_service,
                scm_service,
                cmdb_service,
                self._context.tla,
                self._context.jenkins_build_user_email,
                self._context.parsed_additional_recipients,
                self.SCM_STATUS_TRACKER_REPO,
                self.SCM_STATUS_TRACKER_PATH,
                self.SCM_STATUS_TRACKER_BRANCH_BASE
            )

    def start(self, plan: str):
        """ Starts the decomm change management workflow """
        self._decomm_cm.start(plan)

    def add_execution_details(self, details: str):
        """ Add execution details to the change management issue """
        # update description is not supported in this State
        # so using add comment
        self._decomm_cm.add_comment(details)

    def end(self, is_success: bool = True, error_details: str = None):
        """ Closes the decomm change management issues """
        self._decomm_cm.finish(is_success, error_details)
