# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import environ
from unittest import TestCase

from tladecomm.context import Context


class ContextTest(TestCase):

    def test___init__(self):
        environ['JIRA_ENDPOINT'] = 'dummy'
        environ['JIRA_USERNAME'] = 'dummy'
        environ['JIRA_PASSWORD'] = 'dummy'
        environ['JENKINS_ENDPOINT'] = 'dummy'
        environ['JENKINS_WEBHOOK_TOKEN'] = 'dummy'
        environ['JENKINS_JOB_NAME'] = 'dummy'
        environ['JENKINS_USERNAME'] = 'dummy'
        environ['JENKINS_TOKEN'] = 'dummy'
        environ['CMDB_TYPE'] = 'dummy'
        environ['CMDB_ENDPOINT'] = 'dummy'
        environ['CMDB_USERNAME'] = 'dummy'
        environ['CMDB_PASSWORD'] = 'dummy'
        environ['ISSUE_TRACKER_TYPE'] = 'jira'
        environ['ISSUE_TRACKER_ENDPOINT'] = 'dummy'
        environ['ISSUE_TRACKER_USERNAME'] = 'dummy'
        environ['ISSUE_TRACKER_PASSWORD'] = 'dummy'
        environ['SCM_TYPE'] = 'gitlab'
        environ['SCM_URL'] = 'dummy'
        environ['SCM_TOKEN'] = 'dummy'
        environ['OSP10_USERNAME'] = 'dummy'
        environ['OSP10_PASSWORD'] = 'dummy'
        environ['APPROVAL_ENCRYPTION_KEY'] = 'dummy'
        environ['TLA_NAME'] = 'dummy'
        environ['NFS_VOLUMES'] = 'yes'

        environ['REQUEST_HASH'] = 'dummy'
        context = Context()
        assert context.is_dry_run() is False

        environ['REQUEST_HASH'] = 'DRY-RUN'
        context = Context()
        assert context.is_dry_run() is True

    def test__get_var_or_none(self):
        self.skipTest('NOT TESTED YET')

    def test__parse_additional_recipients(self):
        self.skipTest('NOT TESTED YET')

    def test__validate(self):
        self.skipTest('NOT TESTED YET')

    def test_is_dry_run(self):
        self.skipTest('NOT TESTED YET')

    def test_load_from_dict(self):
        self.skipTest('NOT TESTED YET')
