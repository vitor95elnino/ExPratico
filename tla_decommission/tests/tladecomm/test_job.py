#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
from os import environ
import sys
import unittest
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from catoolkit.service.cmdb.insight_manager import InsightManager
from tladecomm.context import Context
from tladecomm.email_helper import EmailHelper
from tladecomm.job import Job


class JobTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # only runs when all the tests are run
        # if one runs an isolated test, this will not be called
        environ['JIRA_ENDPOINT'] = 'dummy_JIRA_ENDPOINT'
        environ['JIRA_USERNAME'] = 'dummy_JIRA_USERNAME'
        environ['JIRA_PASSWORD'] = 'dummy_JIRA_PASSWORD'
        environ['JENKINS_ENDPOINT'] = 'dummy_JENKINS_ENDPOINT'
        environ['TOKEN_NAME'] = 'dummy_JENKINS_WEBHOOK_TOKEN'
        environ['JENKINS_JOB_NAME'] = 'dummy_JENKINS_JOB_NAME'
        environ['JENKINS_WEBHOOK_TOKEN'] = 'dummy_JENKINS_WEBHOOK_TOKEN'
        environ['JENKINS_USERNAME'] = 'dummy_JENKINS_USERNAME'
        environ['JENKINS_TOKEN'] = 'dummy_JENKINS_TOKEN'
        environ['CMDB_TYPE'] = 'dummy_CMDB_CMDB_TYPE'
        environ['CMDB_ENDPOINT'] = 'dummy_CMDB_ENDPOINT'
        environ['CMDB_USERNAME'] = 'dummy_CMDB_USERNAME'
        environ['CMDB_PASSWORD'] = 'dummy_CMDB_PASSWORD'
        environ['ISSUE_TRACKER_TYPE'] = 'dummy_ISSUE_TRACKER_TYPE'
        environ['ISSUE_TRACKER_ENDPOINT'] = 'dummy_ISSUE_TRACKER_ENDPOINT'
        environ['ISSUE_TRACKER_USERNAME'] = 'dummy_ISSUE_TRACKER_USERNAME'
        environ['ISSUE_TRACKER_PASSWORD'] = 'dummy_ISSUE_TRACKER_PASSWORD'
        environ['SCM_TYPE'] = 'dummy_SCM_TYPE'
        environ['SCM_URL'] = 'dummy_SCM_URL'
        environ['SCM_TOKEN'] = 'dummy_SCM_TOKEN'
        environ['OSP10_USERNAME'] = 'dummy_OSP10_USERNAME'
        environ['OSP10_PASSWORD'] = 'dummy_OSP10_PASSWORD'
        environ['BUILD_USER_ID'] = 'dummy_BUILD_USER_ID'
        environ['BUILD_USER_EMAIL'] = 'dummy_BUILD_USER_EMAIL'
        environ[
            'APPROVAL_ENCRYPTION_KEY'] = 'TO_CHANGE_AS_SOON_AS_IT_GOES_TO_PROD'
        environ['TLA_NAME'] = 'dummy_TLA_NAME'
        environ['NFS_VOLUMES'] = 'yes'
        environ['REQUEST_HASH'] = 'DRY-RUN'
        print('setUpClass')

    @patch('tladecomm.guard_helper.InsightManager')
    def test_run(self, mock_insight_manager: MagicMock) -> None:
        self.skipTest('NOT TESTED YET')

        environ['CMDB_TYPE'] = InsightManager.CMDB_TYPE
        mock_insight_manager.return_value = MagicMock()
        mock_insight_manager.return_value.get_type.return_value = \
            InsightManager.CMDB_TYPE

        environ['TLA_NAME'] = 'dummy'

        environ['REQUEST_HASH'] = 'DRY-RUN'
        job = Job()
        job.run()

        # real hash generated with
        # encryption key=TO_CHANGE_AS_SOON_AS_IT_GOES_TO_PROD
        environ[
            'REQUEST_HASH'] = 'L20tJjk0KzQxOiUMPidtdW5ud2FmemRpdHx9fW1ldm1kYWNkdj06Mj0kPTMgOx4xJnF1b2w4LjosI3ZzZ20HBhYYCwAFAQoWCwYbYXJhbCAqNjI5fX9vbQwKCB8bFgEMAh1naX86OjM8fm9mFhoWDwweGxQADR4WEhIGA2xlYXE1JiY4ImEiPDYnDz08Oz9qJDt9Pg=='
        job = Job()
        job.run()

    @patch('tladecomm.guard_helper.InsightManager')
    def test_set_context(self, mock_insight_manager: MagicMock) -> None:
        environ['CMDB_TYPE'] = InsightManager.CMDB_TYPE
        mock_insight_manager.return_value = MagicMock()
        mock_insight_manager.return_value.get_type.return_value = \
            InsightManager.CMDB_TYPE

        job = Job()
        job.set_context()
        self.assertIsInstance(job._context, Context)

    @patch('tladecomm.guard_helper.InsightManager')
    def test_is_dry_run(self,
                        mock_insight_manager: MagicMock
                        ) -> None:
        environ['CMDB_TYPE'] = InsightManager.CMDB_TYPE
        mock_insight_manager.return_value = MagicMock()
        mock_insight_manager.return_value.get_type.return_value = \
            InsightManager.CMDB_TYPE
        environ['REQUEST_HASH'] = 'DRY-RUN'
        job = Job()
        job.set_context()
        self.assertTrue(job.is_dry_run())

        environ['REQUEST_HASH'] = 'NON_DRY_RUN'
        job = Job()
        job.set_context()
        self.assertFalse(job.is_dry_run())

    @patch('tladecomm.guard_helper.InsightManager')
    def test_get_email_helper(
            self,
            mock_insight_manager: MagicMock
    ) -> None:
        environ['CMDB_TYPE'] = InsightManager.CMDB_TYPE
        mock_insight_manager.return_value = MagicMock()
        mock_insight_manager.return_value.get_type.return_value = \
            InsightManager.CMDB_TYPE

        # test success
        job = Job()
        job.set_context()
        self.assertIsInstance(job.get_email_helper(), EmailHelper)
        # test error
        job = Job()
        with self.assertRaises(Exception):
            # Context must be set using set_context() before using EmailHelper
            job.get_email_helper()

    @patch('tladecomm.guard_helper.InsightManager')
    @patch('tladecomm.job.Context.load_from_dict')
    @patch('tladecomm.job.EmailHelper.parse_request_hash')
    def test_load_request_into_context(
            self,
            mock_parse_request_hash,
            mock_load_from_dict,
            mock_insight_manager: MagicMock
    ) -> None:
        environ['CMDB_TYPE'] = InsightManager.CMDB_TYPE
        mock_insight_manager.return_value = MagicMock()
        mock_insight_manager.return_value.get_type.return_value = \
            InsightManager.CMDB_TYPE

        job = Job()
        job.set_context()
        job.load_request_into_context()
        self.assertTrue(
            mock_parse_request_hash.called,
            'Request hash not read'
        )
        self.assertTrue(
            mock_load_from_dict.called,
            'Request hash must be loaded into context'
        )

    def _test_str_input_against_std_output(self,
                                           method_to_test: str,
                                           input_str: str,
                                           str_to_check: str
                                           ) -> None:
        captured_output = io.StringIO()  # Create StringIO object
        sys.stdout = captured_output  # and redirect stdout.
        func = getattr(Job, method_to_test)
        func(input_str)
        self.assertEqual(
            captured_output.getvalue(),
            str_to_check
        )
        sys.stdout = sys.__stdout__  # Reset redirect.

    # other tests - biz related
    @unittest.skip("Sadly cannot check this because don't have BUILD USER")
    def test_try_approve_different_tla(self):
        """
        If someone try to change the approval URL to another TLA
        the system must deny that run due to the TLA name
        included in the encrypted data
        """

        # Sadly cannot check this because jenkins don't set the BUILD_USER var
        # when the job is triggered remotely
        self.skipTest('NOT TESTED YET')

    def test___init__(self):
        self.skipTest('Constructor method')

    def test__create_email_helper(self):
        self.skipTest('NOT TESTED YET')

    def test__create_guard_helper(self):
        self.skipTest('NOT TESTED YET')

    def test__create_change_manager_helper(self):
        self.skipTest('NOT TESTED YET')

    def test_get_guard_helper(self):
        self.skipTest('NOT TESTED YET')

    def test_get_change_manager_helper(self):
        self.skipTest('NOT TESTED YET')

    def test__create_decomm_helper(self):
        self.skipTest('NOT TESTED YET')

    def test_get_decomm_helper(self):
        self.skipTest('NOT TESTED YET')
