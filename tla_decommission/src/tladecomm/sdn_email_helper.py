import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from catoolkit.service.cmdb.insight_service import InsightService
from catoolkit.library.utils.loggable import Loggable
from tladecomm.get_sdn_rules import SourceGraphClient

def create_subject(tla):
    return f"Action Needed: Delete SDN Rule for the target {tla}"

class EmailSdnHelper(Loggable):
    def __init__(self, sg_client: SourceGraphClient, insight_service: InsightService, smtp_server: str, smtp_port: int, sender_email: str):
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
        """
        Fetches SDN rules for a given TLA name using the SourceGraphClient.
        """
        data = self._sg_client.get_sdn_rules(tla_name)
        return self._sg_client.process_data(data, tla_name)

    def get_tla_people(self, tla_name: str) -> dict:
        """
        Retrieves and processes people associated with TLAs that use the TLA to be decommed as a target.
        """
        all_people = {}
        tla_list = self.fetch_sdn_rules(tla_name)

        for tla in tla_list:
            self._logger.info(f"Processing TLA: {tla}")
            if tla in all_people:
                self._logger.info(f"TLA {tla} already processed. Skipping.")
                continue

            try:
                tla_people = self._insight_service.get_tla_people(tla)
                all_people[tla] = tla_people

                formatted_people = {}
                for key, value in tla_people.items():
                    if isinstance(value, list):
                        formatted_people[key] = [
                            vars(person) if hasattr(person, "__dict__") else str(person) for person in value
                        ]
                    else:
                        formatted_people[key] = value

                all_people[tla] = formatted_people
                self._logger.info(f"Processed TLA {tla} people: {formatted_people}")
            except Exception as error:
                self._logger.error(f"Error getting the owners in Jira of the {tla}: {error}")

        return all_people

    def get_emails(self, tla_name: str) -> list:
        """
        Gets the list of emails to the owners of the SDN rule being decommissioned.
        """
        all_people = self.get_tla_people(tla_name)
        emails = []
        for tla, people_data in all_people.items():
            for role, people_list in people_data.items():
                if not isinstance(people_list, list):
                    continue

                for person in people_list:
                    if not isinstance(person, dict):
                        continue

                    email = person.get('email')
                    emails.append(email)
        return emails

    def send_email(self, tla_name):
        """
        This function gets all the data to the trigger_an_email function

        :param tla_name: The TLA name that is beind decommissioned.
        """
        list_of_emails = self.get_sdn_emails(tla_name)
        subject = create_subject(tla_name)
        message_body = self.create_message_body(tla_name)
        self.trigger_an_email(list_of_emails, subject, message_body)

    def create_message_body(self, tla_name):
        """
        Reads the HTML template from the file system, replaces placeholders, and returns the message body.
        """
        base_dir = os.getenv("BASE_DIR", ".")
        template_path = os.path.join(base_dir, "var", "emails", "html_sdn.html.j2")

        try:
            with open(template_path, "r") as file:
                html_template = file.read()
        except FileNotFoundError:
            self._logger.error(f"Template file not found at {template_path}.")
            return ""

        # Replace placeholders with actual values(tla_name and i2_support slack channel)
        return html_template.replace("{{ tla }}", tla_name).replace("{{ url }}","https://betfair.slack.com/archives/C04N7BRSK")

    def get_sdn_emails(self, tla_name: str):
        """
        Retrieves email addresses of people associated with the given TLA.

        :param tla_name: The TLA name to fetch email addresses for.
        :return: A list of email addresses.
        """
        # Uses inherited methods from SdnHelper
        return self.get_emails(tla_name)

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
                    msg = MIMEMultipart()
                    msg['From'] = self.smtp_config['sender_email']
                    msg['To'] = email
                    msg['Subject'] = subject

                    # Attach the HTML body to the email
                    html_part = MIMEText(message_body, 'html')
                    msg.attach(html_part)

                    # Send the email
                    server.send_message(msg)
                    self._logger.info(f"Email sent to {email}")

        except Exception as e:
           self._logger.error(f"An error occurred while sending email: {e}")

