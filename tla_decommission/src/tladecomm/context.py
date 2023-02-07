#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from email.utils import parseaddr
from os import environ
from typing import Optional

from catoolkit.library.utils.loggable import Loggable
from catoolkit.library.utils.validator import Validator


class Context(Loggable):
    """A class to load all the environment variables that are needed for this
    script

    If any of the string variables are missing then the name
    of the missing var will be printed and the script will exit.
    """
    REQUEST_HASH_DRY_RUN = 'DRY-RUN'
    PARAMS_COMMENT_SYMBOL = '#'
    PARAMS_LINE_SEPARATOR = '\n'
    # job related
    KEY_TLA_NAME = 'TLA_NAME'
    NFS_VOLUMES_DECOMM = 'NFS_VOLUMES'
    # to be passed in encrypted URL
    KEY_APPROVED_TLA_NAME = 'APPROVED_TLA_NAME'
    KEY_REQUEST_HASH = 'REQUEST_HASH'
    KEY_APPROVAL_ENCRYPTION_KEY = 'APPROVAL_ENCRYPTION_KEY'
    KEY_ADDITIONAL_RECIPIENTS = 'ADDITIONAL_RECIPIENTS'
    # jenkins related
    KEY_JENKINS_ENDPOINT = 'JENKINS_ENDPOINT'
    KEY_JENKINS_AUT_ENDPOINT = 'JENKINS_AUT_ENDPOINT'
    KEY_JENKINS_WEBHOOK_TOKEN = 'JENKINS_WEBHOOK_TOKEN'
    KEY_JENKINS_JOB_NAME = 'JENKINS_JOB_NAME'
    KEY_JENKINS_USERNAME = 'JENKINS_USERNAME'
    KEY_JENKINS_PASSWORD = 'JENKINS_PASSWORD'
    # cmdb
    KEY_CMDB_TYPE = 'CMDB_TYPE'
    KEY_CMDB_ENDPOINT = 'CMDB_ENDPOINT'
    KEY_CMDB_USERNAME = 'CMDB_USERNAME'
    KEY_CMDB_PASSWORD = 'CMDB_PASSWORD'
    # issue tracker
    KEY_ISSUE_TRACKER_TYPE = 'ISSUE_TRACKER_TYPE'
    KEY_ISSUE_TRACKER_ENDPOINT = 'ISSUE_TRACKER_ENDPOINT'
    KEY_ISSUE_TRACKER_USERNAME = 'ISSUE_TRACKER_USERNAME'
    KEY_ISSUE_TRACKER_PASSWORD = 'ISSUE_TRACKER_PASSWORD'
    # scm
    KEY_SCM_TYPE = 'SCM_TYPE'
    KEY_SCM_URL = 'SCM_URL'
    KEY_SCM_TOKEN = 'SCM_TOKEN'
    # osp10
    KEY_OSP16_USERNAME = 'OSP16_USERNAME'
    KEY_OSP16_PASSWORD = 'OSP16_PASSWORD'
    # build related
    KEY_BUILD_USER_ID = 'BUILD_USER_ID'
    KEY_BUILD_USER_EMAIL = 'BUILD_USER_EMAIL'
    # extra
    KEY_REQUESTED_AT = 'requested_at'
    KEY_REQUESTED_BY = 'requested_by'

    def __init__(self):
        super().__init__()
        # don't even compute arguments if debug is not enabled
        if self._is_log_debug_enabled():
            for item, value in environ.items():
                # Debug all environment variables
                self._logger.debug(f'{item}: {value}')

        # String env vars
        try:
            # Always required vars
            self.tla = environ[self.KEY_TLA_NAME]
            self.request_hash = environ[self.KEY_REQUEST_HASH]
            self.approval_encryption_key = \
                environ[self.KEY_APPROVAL_ENCRYPTION_KEY]
            self.nfs_volumes_decomm = environ[self.NFS_VOLUMES_DECOMM]
            # jenkins related
            self.jenkins_endpoint = environ[self.KEY_JENKINS_AUT_ENDPOINT]
            self.jenkins_webhook_token = \
                environ[self.KEY_JENKINS_WEBHOOK_TOKEN]
            self.jenkins_job_name = environ[self.KEY_JENKINS_JOB_NAME]
            self.jenkins_username = environ[self.KEY_JENKINS_USERNAME]
            self.jenkins_password = environ[self.KEY_JENKINS_PASSWORD]
            # cmdb
            self.cmdb_type = environ[self.KEY_CMDB_TYPE]
            self.cmdb_endpoint = environ[self.KEY_CMDB_ENDPOINT]
            self.cmdb_username = environ[self.KEY_CMDB_USERNAME]
            self.cmdb_password = environ[self.KEY_CMDB_PASSWORD]
            # issue tracker
            self.issue_tracker_type = environ[self.KEY_ISSUE_TRACKER_TYPE]
            self.issue_tracker_endpoint = environ[
                self.KEY_ISSUE_TRACKER_ENDPOINT]
            self.issue_tracker_username = environ[
                self.KEY_ISSUE_TRACKER_USERNAME]
            self.issue_tracker_password = environ[
                self.KEY_ISSUE_TRACKER_PASSWORD]
            # SCM
            self.scm_type = environ[self.KEY_SCM_TYPE]
            self.scm_url = environ[self.KEY_SCM_URL]
            self.scm_token = environ[self.KEY_SCM_TOKEN]
            # OSP 16
            self.osp16_username = environ[self.KEY_OSP16_USERNAME]
            self.osp16_password = environ[self.KEY_OSP16_PASSWORD]

            # Required depending on the job step (dry-run vs real)
            # some of these vars will be provided by the REQUEST HASH
            # when invoked remotely, BUILD_USER* will be empty
            # (even if no anonymous triggers are allowed in jenkins)
            self.approved_tla_name = \
                self._get_var_or_none(self.KEY_APPROVED_TLA_NAME)
            self.request_additional_recipients = \
                self._get_var_or_none(self.KEY_ADDITIONAL_RECIPIENTS)
            self.jenkins_build_user_id = \
                self._get_var_or_none(self.KEY_BUILD_USER_ID)
            self.jenkins_build_user_email = \
                self._get_var_or_none(self.KEY_BUILD_USER_EMAIL)
            self.request_requested_at = \
                self._get_var_or_none(self.KEY_REQUESTED_AT)
            self.request_requested_by = \
                self._get_var_or_none(self.KEY_REQUESTED_BY)

            # will set self.parsed_additional_recipients
            self._parse_additional_recipients()

        except KeyError as ke:
            raise Exception(f"ERROR - env var '{ke.args[0]}' is missing")

        # normalize tla name
        self.tla = self.tla.lower().strip(' ')
        if self.approved_tla_name:
            self.approved_tla_name = self.tla.lower().strip(' ')

        # validate full info
        self._validate()

    def _get_var_or_none(self, varname: str) -> Optional[str]:
        result = environ.get(varname)  # default None
        if '' == result:
            result = None
            # deal with jenkins limitation sending empty instead of None
        return result

    def _parse_additional_recipients(self):
        self.parsed_additional_recipients = []
        if self.request_additional_recipients is None:
            return
        for email_address in self.request_additional_recipients.splitlines():
            if email_address.startswith(self.PARAMS_COMMENT_SYMBOL):
                continue
            email_address_parts = parseaddr(email_address)
            # Returns a tuple of that information,
            # unless the parse fails, in which case a
            # 2-tuple of ('', '') is returned.
            if Validator.validate_email(email_address_parts[1]):
                self.parsed_additional_recipients.append(
                    email_address_parts[1]
                )
        self._logger.debug(self.parsed_additional_recipients)

    def _validate(self):
        """Iterate through all of this class's STRING attributes and verify
        that none of them are empty
        """
        for attr, value in vars(self).items():
            if isinstance(value, str) and value.strip() == '':
                raise Exception(f"ERROR - Variable '{attr}' cannot be empty.")

    def is_dry_run(self) -> bool:
        return self.REQUEST_HASH_DRY_RUN == self.request_hash

    def load_from_dict(self, data_to_load: dict):
        if self.is_dry_run():
            # load from request has only when it's a real request, not dry-run
            # In the case of dry-run, all parameters must be provided
            # by environment vars
            return

        self.approved_tla_name = \
            data_to_load.get(
                self.KEY_APPROVED_TLA_NAME,
                self.approved_tla_name
            )
        self.jenkins_build_user_id = \
            data_to_load.get(
                self.KEY_BUILD_USER_ID,
                self.jenkins_build_user_id
            )
        self.jenkins_build_user_email = \
            data_to_load.get(
                self.KEY_BUILD_USER_EMAIL,
                self.jenkins_build_user_email
            )
        self.request_additional_recipients = \
            data_to_load.get(
                self.KEY_ADDITIONAL_RECIPIENTS,
                self.request_additional_recipients
            )
        self.request_requested_at = \
            data_to_load.get(self.KEY_REQUESTED_AT, self.request_requested_at)
        self.request_requested_by = \
            data_to_load.get(self.KEY_REQUESTED_BY, self.request_requested_by)
        self._parse_additional_recipients()

        self._validate()
