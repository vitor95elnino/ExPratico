from catoolkit.service.cmdb.insight_service import InsightService
from catoolkit.service.cmdb.insight_service_arguments import InsightServiceArguments
from get_sdn_rules import get_sdn_rules, process_data
import os
#JIRA CREDENTIALS
jira_endpoint = os.getenv('JIRA_ENDPOINT')
jira_username = os.getenv('JIRA_USERNAME')
jira_password = os.getenv('JIRA_PASSWORD')

class SdnHelper:
    def __init__(self, insight_service):
        self.job = None
        self._insight_service = insight_service
        self.tla_name = "detestrita"

    def fetch_sdn_rules(self):
        data = get_sdn_rules(self.tla_name)
        return process_data(data, self.tla_name)

    def get_tla_people(self):
        all_people = {}
        tla_list = self.fetch_sdn_rules()
        print("Initial TLA list:", tla_list)  #

        for tla in tla_list:
            print(f"Processing TLA: {tla}")
            if tla in all_people:
                print(f"TLA {tla} already processed. Skipping.")
                continue  # ter a certeza que nao esta em loop

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
            print(f"Processed TLA {tla} people: {formatted_people}")
        return all_people

    def get_emails(self):
        all_people = self.get_tla_people()
        emails = []
        for tla, people_data in all_people.items():
            for role, people_list in people_data.items():
                if isinstance(people_list, list):
                    # Extract emails from each person's attributes
                    for person in people_list:
                        if isinstance(person, dict):
                            email = person.get('email')
                            if email and email != 'N/A':  # Only add valid emails
                                emails.append(email)
        return emails

    def main(self):
        self.fetch_sdn_rules()
        self.get_emails()


if __name__ == '__main__':
    # Create InsightServiceArguments with appropriate values
    insight_service_args = InsightServiceArguments(
        endpoint=jira_endpoint,
        username=jira_username,
        password=jira_password,
        object_schema_id=11,
    )

    # Initialize the InsightService with valid arguments
    insight_service = InsightService(insight_service_args)

    # Pass the InsightService instance to SdnHelper
    helper = SdnHelper(insight_service)
    helper.main()