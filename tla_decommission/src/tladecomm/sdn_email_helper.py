import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from catoolkit.service.cmdb.insight_service import InsightService
from catoolkit.service.cmdb.insight_service_arguments import InsightServiceArguments
from tla_decommission.src.tladecomm.get_sdn_rules import tla_name
from tla_decommission.src.tladecomm.sdn_helper import SdnHelper
#JIRA CREDENTIALS
jira_endpoint = os.getenv('JIRA_ENDPOINT')
jira_username = os.getenv('JIRA_USERNAME')
jira_password = os.getenv('JIRA_PASSWORD')

def create_subject(tla):
    return f"Action Needed: Delete SDN Rule for the target {tla}"


class EmailSdnHelper(SdnHelper):
    def __init__(self, insight_service, smtp_config):
        insight_service_args = InsightServiceArguments(
            endpoint=jira_endpoint,
            username=jira_username,
            password=jira_password,
            object_schema_id=11
        )
        insight_service = InsightService(insight_service_args)
        super().__init__(insight_service)

        self.smtp_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'ie1-mail-prd.prd.betfair'),
            'port': int(os.getenv('SMTP_PORT', 25)),
            'sender_email': os.getenv('SENDER_EMAIL', 'cloud.automation@paddypowerbetfair.com'),
        }
        self.tla_name = os.getenv('TLA_NAME')

    def send_email(self, tla_name):
        list_of_emails = self.get_sdn_emails()  # Get the emails for the current TLA
        print(f"Emails to send: {list_of_emails}")
        subject = create_subject(tla_name)
        message_body = self.create_message_body(tla_name)
        self.trigger_an_email(list_of_emails, subject, message_body)

    def create_message_body(self, tla_name):
        """
        Reads the HTML template from the file system, replaces placeholders, and returns the message body.
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                                ".."))  # the directory is not the same as the one in the snippet
        template_path = os.path.join(base_dir, "var", "emails", "html_sdn.html")

        try:
            with open(template_path, "r") as file:
                html_template = file.read()
        except FileNotFoundError:
            print(f"Template file not found at {template_path}.")
            return ""

        # Replace placeholders with actual values
        return html_template.replace("{{ tla }}", tla_name)

    def get_sdn_emails(self):
        # Uses inherited methods from SdnHelper
        return self.get_emails()

    def trigger_an_email(self, list_of_emails, subject, message_body):
        """
        Sends an email to a list of recipients.

        :param list_of_emails: List of email addresses to send the email to.
        :param subject: Subject of the email.
        :param message_body: Body of the email.
        """
        try:
            # Set up the SMTP connection
            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['port']) as server:

                for email in list_of_emails:
                    print(f"Sending email to {email}")
                    msg = MIMEMultipart()
                    msg['From'] = self.smtp_config['sender_email']
                    msg['To'] = email
                    msg['Subject'] = subject

                    # Attach the HTML body to the email
                    html_part = MIMEText(message_body, 'html')
                    msg.attach(html_part)

                    # Send the email
                    server.send_message(msg)
                    print(f"Email sent to {email}")

        except Exception as e:
            print(f"An error occurred while sending email: {e}")
