from os import environ
from sys import exit
from jira import JIRA

JIRA_ENDPOINT = environ.get('JIRA_ENDPOINT')
options = { 'server': JIRA_ENDPOINT }
JIRA_USERNAME = environ.get('JIRA_USERNAME')
JIRA_PASSWORD = environ.get('JIRA_PASSWORD')
CHANGE_ID = environ.get('CHANGE_ID')
AZ_OSP16 = environ.get('AZ_OSP16')
VALID_APPROVAL_STATE = 'In Progress'

def main():
    """Validate change id status"""
    print('Validating CHANGE_ID...')

    # Jira connection
    try:
        jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))
    except Exception as e:
        print(f'Failed to connect to Jira, error: {e}')
        exit(1)

    # Search issue
    if not CHANGE_ID:
        print('CHANGE_ID not found, please set a valid CHANGE_ID')
        exit(1)
    try:
        issue = jira.issue(CHANGE_ID)
    except Exception as e:
        print(f'CHANGE_ID is {CHANGE_ID} not found or invalid, error: {e}')
        exit(1)

    status = issue.fields.status.name
    technical_service = issue.fields.customfield_32451[0]
    print(f'Technical service is {technical_service}')

    if status != VALID_APPROVAL_STATE:
        print(f'Failed approval state. CHANGE_ID is {CHANGE_ID} is {status}, should be {VALID_APPROVAL_STATE}')
        exit(1)
    
    print(f'CHANGE_ID {CHANGE_ID} is valid and in progress')
    exit(0)


if __name__ == '__main__':
    if AZ_OSP16 == 'prd':
        main()
    exit(0)
