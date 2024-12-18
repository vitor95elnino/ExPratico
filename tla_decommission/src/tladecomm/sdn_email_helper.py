import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from catoolkit.library.utils.loggable import Loggable
from catoolkit.service.cmdb.insight_service import InsightService
from catoolkit.service.cmdb.insight_service_arguments import InsightServiceArguments
from get_sdn_rules import SourceGraphClient
from os import getenv

def create_subject(tla):
    return f"Action Needed: Delete SDN Rule for the target {tla}"


class EmailSdnHelper(Loggable):
    def __init__(self, insight_service: InsightService, smtp_server: str, smtp_port: int, sender_email: str):
        super().__init__()

        self.job = None
        self._insight_service = insight_service
        self._sg_client = sg_client

        self.smtp_config = {
            'smtp_server': smtp_server,
            'port': smtp_port,
            'sender_email': sender_email,
        }

    def fetch_sdn_rules(self, tla_name: str):
        data = self._sg_client.get_sdn_rules(tla_name)
        return self._sg_client.process_data(data, tla_name)

    def get_tla_people(self, tla_name: str) -> dict:
        all_people = {}
        tla_list = self.fetch_sdn_rules(tla_name)
        self._logger.info("Initial TLA list:", tla_list)

        for tla in tla_list:
            self._logger.info(f"Processing TLA: {tla}")
            if tla in all_people:
                self._logger.info(f"TLA {tla} already processed. Skipping.")
                continue  #@FIXME ter a certeza que nao esta em loop

            tla_people = self._insight_service.get_tla_people(tla)
            all_people[tla] = tla_people
            # Format the people data for stop the memory identifiers
            formatted_people = {}
            for key, value in tla_people.items():
                if isinstance(value, list):  # Sees if is a list
                    formatted_people[key] = [
                        vars(person) if hasattr(person, "__dict__") else str(person) for person in value
                    ]
                else:
                    formatted_people[key] = value  # For non-list values, keep as-is

            all_people[tla] = formatted_people
            self._logger.info(f"Processed TLA {tla} people: {formatted_people}")
        return all_people

    def get_emails(self, tla_name: str) -> list:
        all_people = self.get_tla_people(tla_name)
        emails = []
        for tla, people_data in all_people.items():
            for role, people_list in people_data.items():
                if not isinstance(people_list, list):
                    continue

                # Extract emails from each person's attributes
                for person in people_list:
                    if not isinstance(person, dict):
                        continue

                    # @TODO test/check if the condition "email != 'N/A'" is needed
                    email = person.get('email')
                    if email and email != 'N/A':  # Only add valid emails
                        emails.append(email)
        return emails

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

if __name__ == '__main__':
    smtp_server = os.getenv('SMTP_SERVER', 'ie1-mail-prd.prd.betfair')
    port = int(os.getenv('SMTP_PORT', 25))
    sender_email = os.getenv('SENDER_EMAIL', 'cloud.automation@paddypowerbetfair.com')

    jira_endpoint = getenv('JIRA_ENDPOINT')
    jira_username = getenv('JIRA_USERNAME')
    jira_password = getenv('JIRA_PASSWORD')

    sourcegraph_api = getenv('SOURCEGRAPH_API')
    access_token = getenv('SOURCEGRAPH_TOKEN')

    tla_name = getenv('TLA_NAME', 'detestrg')

    # Create InsightServiceArguments with appropriate values
    insight_service_args = InsightServiceArguments(
        endpoint=jira_endpoint,
        username=jira_username,
        password=jira_password,
        object_schema_id=11,
    )

    # Initialize the InsightService with valid arguments
    insight_service = InsightService(insight_service_args)
    sg_client = SourceGraphClient(sourcegraph_api, access_token)

    esh = EmailSdnHelper(insight_service, smtp_server, port, sender_email)
    esh.send_email(tla_name)
