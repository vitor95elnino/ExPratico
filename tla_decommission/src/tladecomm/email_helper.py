#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from typing import Dict
from typing import List

from catoolkit.library.utils.loggable import Loggable
from catoolkit.model.email.email_generator import EmailGenerator
from catoolkit.model.email.recipients_list import RecipientList
from catoolkit.model.email.url_generator import UrlGenerator
from tladecomm.context import Context


class EmailHelper(Loggable):
    """Handles all email message logic"""
    JENKINS_WEBHOOK_TOKEN_URL = '{jenkins_url}/job/{jenkins_job_name}/' \
                                'buildWithParameters?' \
                                'REQUEST_HASH={{{{REQUEST_HASH}}}}&' \
                                'token={{{{JENKINS_WEBHOOK_TOKEN}}}}&' \
                                'TLA_NAME={{{{TLA_NAME}}}}&' \
                                'cause=EMAIL_APPROVAL'
    EMAILS_JENKINS_RESULT_PATH = './var/emails/'
    EMAILS_JENKINS_APPROVAL_EMAIL_NAME = 'approval'
    JENKINS_JOB_LOG_URL_TPL = '{jenkins_url}/job/{jenkins_job_name}'

    def __init__(self, context: Context):
        super().__init__()
        self._context = context
        # get the url generator needed to generate or
        # to decrypt the approval url
        self._url_generator = None
        self._url_generator = self.get_url_generator()

    def get_url_generator(self) -> UrlGenerator:
        if self._url_generator is None:
            self._logger.debug(f'Creating Url Generator')
            self._url_generator = UrlGenerator(
                self._context.approval_encryption_key,
                self.JENKINS_WEBHOOK_TOKEN_URL.format(
                    jenkins_url=self._context.jenkins_endpoint,
                    jenkins_job_name=self._context.jenkins_job_name)
            )

        return self._url_generator

    def generate_approval_email(self,
                                recipients: RecipientList,
                                assets_listing: List[Dict]
                                ):
        email_name = self.EMAILS_JENKINS_APPROVAL_EMAIL_NAME
        self._logger.debug(f'Generating approval email {email_name}')
        data_to_encrypt = {
            Context.KEY_REQUESTED_AT: time.time(),
            Context.KEY_REQUESTED_BY: self._context.jenkins_build_user_id,
            Context.KEY_BUILD_USER_ID: self._context.jenkins_build_user_id,
            Context.KEY_BUILD_USER_EMAIL:
                self._context.jenkins_build_user_email,
            # we send the tla name in a different key to allow the comparison
            # (validation) after the approval
            Context.KEY_APPROVED_TLA_NAME: self._context.tla,
            Context.NFS_VOLUMES_DECOMM: self._context.nfs_volumes_decomm,
        }
        # don't encrypt garbage
        if len(self._context.parsed_additional_recipients) > 0:
            self._logger.debug(f'Adding additional email recipients')
            data_to_encrypt[Context.KEY_ADDITIONAL_RECIPIENTS] = \
                Context.PARAMS_LINE_SEPARATOR.join(
                    self._context.parsed_additional_recipients
            )
        else:
            self._logger.debug(f'NO additional email recipients')

        self._logger.debug(f'Encrypting data')
        encrypted_data = self._url_generator.encrypt(data_to_encrypt)
        data_to_send = {
            Context.KEY_REQUEST_HASH: encrypted_data,
            # this should match the KEY_APPROVED_TLA_NAME after the approval
            # unless someone trying to hack changes it
            Context.KEY_TLA_NAME: self._context.tla,
            Context.KEY_JENKINS_WEBHOOK_TOKEN:
                self._context.jenkins_webhook_token
        }
        # generate the approval URL
        self._logger.debug(f'Generating final URL')
        final_url = self._url_generator.generate_url_for_data(data_to_send)

        # generate the job log URL
        self._logger.debug(f'Generating job log URL')
        job_log_url = self.JENKINS_JOB_LOG_URL_TPL.format(
            jenkins_url=self._context.jenkins_endpoint,
            jenkins_job_name=self._context.jenkins_job_name
        )

        self._logger.debug(f'Building email message')
        # generate the email body
        html_gen = EmailGenerator()

        # email variables that can be used as placeholders in templates
        # Template producers must respect these placeholder
        variables = {
            EmailGenerator.TEMPLATE_PLACEHOLDER_TLA: self._context.tla.upper(),
            EmailGenerator.TEMPLATE_PLACEHOLDER_URL_CONFIRM: final_url,
            EmailGenerator.TEMPLATE_PLACEHOLDER_URL_JOB_LOG: job_log_url,
            EmailGenerator.TEMPLATE_PLACEHOLDER_USERNAME:
                self._context.jenkins_build_user_id,
            EmailGenerator.TEMPLATE_PLACEHOLDER_CONTENT:
                self._generate_html_table(assets_listing)
        }

        self._logger.debug(f'Writing email message to filesystem')
        # generate html body
        html = html_gen.get_decomm_approval_email_body(variables)
        f = open(f'{self.EMAILS_JENKINS_RESULT_PATH}{email_name}_body.html',
                 'w')
        f.write(html)
        f.close()

        # generate email subject
        subject = html_gen.get_decomm_approval_email_subject(variables)
        f = open(f'{self.EMAILS_JENKINS_RESULT_PATH}{email_name}_subject.txt',
                 'w')
        f.write(subject)
        f.close()

        # generate recipients list, to be used by the Jenkins job
        f = open(
            f'{self.EMAILS_JENKINS_RESULT_PATH}{email_name}_recipients.csv',
            'w')
        f.write(','.join(recipients))
        f.close()

        self._logger.debug(f'Generating approval email finished')

    def parse_request_hash(self, request_hash: str) -> dict:
        return self._url_generator.decrypt(self._context.request_hash)

    def _generate_html_table(self, assets_listing: List[Dict]):
        if len(assets_listing) < 1:
            self._logger.debug(f'Empty asset list, skipping table generation')
            return ''
        self._logger.debug(
            f'Generating asset list with {len(assets_listing)} entries')

        headers = assets_listing[0].keys()

        html_table = '''
          <table cellpadding="0"
          cellspacing="0"
          width="100%"
          border="0"
          style="color:#000000;font-family:Helvetica;font-size:13px;line-height:22px;table-layout:auto;width:100%;border:none;">
        '''

        html_table = html_table + '''
            <tr style="border-bottom:1px solid #ecedee;text-align:left;padding:5px 0;">
        '''
        for header in headers:
            html_table = html_table + \
                f'<th style="padding: 0 5px 0 0;">{header}</th>'
        html_table = html_table + '''
              </tr>
        '''

        for asset in assets_listing:
            html_table = html_table + '<tr>'
            for asset_dimension in asset.values():
                html_table = html_table + f'<td style="padding: 0 5px 0 0;">' \
                                          f'{asset_dimension}</td>'
            html_table = html_table + '</tr>'

        html_table = html_table + '''
        </table>
        '''
        return html_table
