#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import time
from datetime import datetime

from catoolkit.library.utils.loggable import Loggable
from tladecomm.change_manager_helper import ChangeManagerHelper
from tladecomm.context import Context
from tladecomm.decomm_helper import DecommHelper
from catoolkit.service.cmdb.insight_service_arguments import InsightServiceArguments
from catoolkit.service.cmdb.insight_service import InsightService
from tladecomm.email_helper import EmailHelper
from tladecomm.guard_helper import GuardHelper

from src.tladecomm.get_sdn_rules import SourceGraphClient
from tla_decommission.src.tladecomm.sdn_email_helper import EmailSdnHelper


class Job(Loggable):
    # http://patorjk.com/software/taag/#p=display&f=Big%20Money-ne&t=DECOMM
    REAL_RUN_ASCII_ART = r'''
     /$$$$$$$  /$$$$$$$$  /$$$$$$   /$$$$$$  /$$      /$$ /$$      /$$
    | $$__  $$| $$_____/ /$$__  $$ /$$__  $$| $$$    /$$$| $$$    /$$$
    | $$  \ $$| $$      | $$  \__/| $$  \ $$| $$$$  /$$$$| $$$$  /$$$$
    | $$  | $$| $$$$$   | $$      | $$  | $$| $$ $$/$$ $$| $$ $$/$$ $$
    | $$  | $$| $$__/   | $$      | $$  | $$| $$  $$$| $$| $$  $$$| $$
    | $$  | $$| $$      | $$    $$| $$  | $$| $$\  $ | $$| $$\  $ | $$
    | $$$$$$$/| $$$$$$$$|  $$$$$$/|  $$$$$$/| $$ \/  | $$| $$ \/  | $$
    |_______/ |________/ \______/  \______/ |__/     |__/|__/     |__/
    '''  # nopep8

    DRY_RUN_ASCII_ART = r'''
     /$$$$$$$  /$$$$$$$  /$$     /$$       /$$$$$$$  /$$   /$$ /$$   /$$
    | $$__  $$| $$__  $$|  $$   /$$/      | $$__  $$| $$  | $$| $$$ | $$
    | $$  \ $$| $$  \ $$ \  $$ /$$/       | $$  \ $$| $$  | $$| $$$$| $$
    | $$  | $$| $$$$$$$/  \  $$$$/        | $$$$$$$/| $$  | $$| $$ $$ $$
    | $$  | $$| $$__  $$   \  $$/         | $$__  $$| $$  | $$| $$  $$$$
    | $$  | $$| $$  \ $$    | $$          | $$  \ $$| $$  | $$| $$\  $$$
    | $$$$$$$/| $$  | $$    | $$          | $$  | $$|  $$$$$$/| $$ \  $$
    |_______/ |__/  |__/    |__/          |__/  |__/ \______/ |__/  \__/
    '''  # nopep8

    def __init__(self):
        super().__init__()
        self._context: Context = None
        self._guard_helper: GuardHelper = None
        self._email_helper: EmailHelper = None
        self._change_man_helper: ChangeManagerHelper = None

    def _create_decomm_helper(self):
        self._decomm_helper = DecommHelper(self._context)

    def _create_email_helper(self):
        self._email_helper = EmailHelper(self._context)

    def _create_guard_helper(self):
        self._guard_helper = GuardHelper(self._context)

    def _create_change_manager_helper(self):
        self._change_man_helper = ChangeManagerHelper(self._context)

    def get_guard_helper(self) -> GuardHelper:
        if self._guard_helper is None:
            raise Exception(
                f'Context must be set using setContext() '
                f'before using GuardHelper')
        return self._guard_helper

    def get_email_helper(self) -> EmailHelper:
        if self._email_helper is None:
            raise Exception(
                f'Context must be set using setContext() '
                f'before using EmailHelper')
        return self._email_helper

    def get_decomm_helper(self) -> DecommHelper:
        if self._decomm_helper is None:
            raise Exception(
                f'Context must be set using setContext() '
                f'before using DecommHelper')
        return self._decomm_helper

    def get_change_manager_helper(self) -> ChangeManagerHelper:
        if self._change_man_helper is None:
            raise Exception(
                f'Context must be set using setContext() '
                f'before using ChangeManagerHelper')
        return self._change_man_helper

    def set_context(self,
                    context: Context = None
                    ) -> Context:
        self._context = context
        if self._context is None:
            self._context = Context()
        self._create_email_helper()
        self._create_guard_helper()
        self._decomm_helper = None
        # it's not possible to initialize decomm helper yet because emails hash
        # is needed
        self._change_man_helper = None
        # do not create change manager helper yet, sometimes is not needed
        return self._context

    def is_dry_run(self):
        return self._context.is_dry_run()

    def load_request_into_context(self):
        """Loads Request information into Context object

        When receiving the approval request (email click) some information
        needs to be retrieved from the encrypted link. In order to
        have always the same behaviour, we are adding all information
        to the context object
        """
        decrypted_data = self.get_email_helper().parse_request_hash(
            self._context.request_hash)
        self._context.load_from_dict(
            decrypted_data
        )

    def run(self,
            context=None,
            approval_expiration_time: int = None
            ) -> None:
        """Runs the job"""
        # default exit code
        exit_code = 1  # Error

        # Set or create context; will raise an exception if invalid
        self._logger.info('Setting job context...')
        self.set_context(context)

        self._logger.info(f'Decomm job for {self._context.tla} starting...')

        if self.is_dry_run():
            '''
            Print what the job would do, but don't actually trigger any jobs
            '''
            self._logger.info(self.DRY_RUN_ASCII_ART)

            # Check if user can run this job
            if self.get_guard_helper().is_this_job_allowed_to_run():
                # Get and list assets to be decommissioned
                self._logger.info(f'LISTING ALL ASSETS')
                self._create_decomm_helper()
                all_assets_list = self.get_decomm_helper().dry_run()
# not introducing additional_recipients into recipients list yet, due to Bug 1178032
                # recipients = self._context.parsed_additional_recipients
                # recipients.extend([self._context.jenkins_build_user_email])
                self._logger.info(f'Building approval email')
                self._logger.debug(all_assets_list)
                self.get_email_helper().generate_approval_email(
                    # recipients,
                    [self._context.jenkins_build_user_email],
                    all_assets_list
                )
                exit_code = 0  # Success
            else:
                self._logger.info(
                    f'The requirements to run {self._context.tla}\'s '
                    f'decommission are not met')
                exit_code = 1  # Error

        else:
            '''
            Do real actions
            '''
            self._logger.info(self.REAL_RUN_ASCII_ART)
            self._logger.info(f'Context HASH: {self._context.request_hash}')

            # enrich the context with Request info
            self.load_request_into_context()
            # now it's possible to initialize decomm helper
            self._create_decomm_helper()

            # Initialize the SourceGraphClient
            job_sg_client = SourceGraphClient(
                sourcegraph_api=self._context.sourcegraph_api,
                access_token=self._context.sourcegraph_token
            )

            # Initialize insight service
            insight_service_args = InsightServiceArguments(
                endpoint=self._context.jira_endpoint,
                username=self._context.jira_username,
                password=self._context.jira_password,
                object_schema_id=11,
            )
            job_insight_service = InsightService(insight_service_args)

            # Initialize EmailSdnHelper
            email_sdn_helper = EmailSdnHelper(
                sg_client=job_sg_client,
                insight_service=job_insight_service,
                smtp_server=self._context.smtp_server,
                smtp_port=self._context.smtp_port,
                sender_email=self._context.sender_email
            )

            # Trigger the email for the sdn rules
            email_sdn_helper.send_email(tla_name=self._context.tla)

            requested_at = self._context.request_requested_at
            approved_at = time.time()
            if self.get_guard_helper().is_this_job_allowed_to_run(
                    requested_at,
                    approved_at,
                    approval_expiration_time
            ):
                requested_by = self._context.request_requested_by
                self._logger.info(f'Original request by: {requested_by}')
                self._logger.info(
                    f'Approved by: {self._context.jenkins_build_user_id}')
                self._logger.info(
                    f'Approved at: {datetime.fromtimestamp(approved_at)}')

                try:
                    self._create_change_manager_helper()

                    # start change management actions
                    # TODO: improve output formats
                    # TODO: handle errors, send to CM
                    decomm_plan = self.get_decomm_helper().dry_run()
                    self.get_change_manager_helper().start(
                        json.dumps(decomm_plan))

                    # Call methods to create the warning email for the sdn rules
                    email_sdn_helper.send_email(tla_name=self._context.tla)

                    decomm_results = self.get_decomm_helper().run()

                    self._logger.debug(decomm_results)

                    jira_pretty_text: str = \
                        f'Triggered {len(decomm_results)} tasks'
                    for (result, url) in decomm_results:
                        jira_pretty_text = jira_pretty_text + \
                                           f'\n{result} - {url}'
                    self.get_change_manager_helper(). \
                        add_execution_details(jira_pretty_text)

                    # close change management actions
                    self.get_change_manager_helper().end()
                    exit_code = 0  # Success
                except RuntimeError as fatal_exception:
                    self._logger.error(f'Aborting due to an error: '
                                       f'{fatal_exception}')
                    self.get_change_manager_helper().end(False, str(fatal_exception))
                    exit_code = 1  # Error

            else:
                self._logger.info(
                    f'The requirements to run {self._context.tla}\'s '
                    f'decommission are not met')
                exit_code = 1  # Error

        sys.exit(exit_code)
