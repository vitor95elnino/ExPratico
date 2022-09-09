#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import time

from tladecomm.email_helper import EmailHelper


class EmailHelperTest(TestCase):

    @patch('tladecomm.email_helper.UrlGenerator')
    def test_get_url_generator(self, mock_url_generator):
        context = MagicMock()
        context.approval_encryption_key.return_value = 'key1'
        context.approval_encryption_key.jenkins_endpoint.return_value = \
            'jenkins_endpoint1'
        context.approval_encryption_key.jenkins_job_name.return_value = \
            'jenkins_job_name1'
        email_helper = EmailHelper(context)

        self.assertIsInstance(email_helper, EmailHelper)
        self.assertEqual(mock_url_generator.call_count, 1)
        # TODO: improve this test, check calls and arguments

    def test_generate_approval_email(self):
        context = MagicMock()
        context.approval_encryption_key.return_value = 'key1'
        context.approval_encryption_key.jenkins_endpoint.return_value = \
            'jenkins_endpoint1'
        context.approval_encryption_key.jenkins_job_name.return_value = \
            'jenkins_job_name1'

        email_helper = EmailHelper(context)
        email_helper.generate_approval_email(['oliveira'], [{'ie1dev':'refbang-qa-1'}])
        self.assertEqual('', 'asd')

    @patch('tladecomm.email_helper.UrlGenerator')
    def test_parse_request_hash(self, mock_url_generator):
        #email_helper = EmailHelper()
        # email_helper.parse_request_hash('hash1')

        #self.assertEqual(mock_url_generator.call_count, 1)
        self.skipTest('NOT TESTED YET')

    def test___init__(self):
        self.skipTest('Constructor method')

    def test__generate_html_table(self):
        self.skipTest('NOT TESTED YET')
