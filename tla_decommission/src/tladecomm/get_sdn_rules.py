import os
import requests

sourcegraph_api = os.getenv('SOURCEGRAPH_API')
tla_name = os.getenv('TLA_NAME')  # tla to be decommissioned
access_token = os.getenv('SOURCEGRAPH_TOKEN')

def get_sdn_rules(tla_name):
    headers = {
        'Authorization': 'token ' + access_token,
        'Content-Type': 'application/json'
    }

    data_sdn = f'{{"query":"query {{ search(query: \\"repo:^gitlab.app.betfair/i2/ file:sdn/defaults.yml target: tla_{tla_name} \\") {{ results {{ results {{ ... on FileMatch {{ repository {{ name }} file {{ path }} lineMatches {{ preview lineNumber }} }} }} }} }} }}","variables":null}}'

    response = requests.post(sourcegraph_api, data=data_sdn, headers=headers)
    print(response.json())
    return response.json()

def process_data(data, tla_name):
    tlas_using_target = []
    for result in data['data']['search']['results']['results']:
        print(result, '1')
        for line_match in result['lineMatches']:
            print(line_match, '2')
            if f'target: tla_{tla_name}' in line_match['preview']:
                tlas_using_target.append(result['repository']['name'].split('/')[-1])
    return tlas_using_target

if __name__ == '__main__':
    data = get_sdn_rules(tla_name)
    tlas = process_data(data, tla_name)

