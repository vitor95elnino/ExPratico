from requests import post

class SourceGraphClient:
    def __init__(self, sourcegraph_api: str, access_token: str):
        self.sourcegraph_api = sourcegraph_api
        self.access_token = access_token

    def get_sdn_rules(self, tla_name: str) -> dict:
        """
        Fetches SDN rules for a given TLA name from the SourceGraph API.
        """
        headers = {
              'Authorization': f'token {self.access_token}',
              'Content-Type': 'application/json'
         }

        data_sdn = f'{{"query":"query {{ search(query: \\"repo:^gitlab.app.betfair/i2/ file:sdn/defaults.yml target: tla_{tla_name} \\") {{ results {{ results {{ ... on FileMatch {{ repository {{ name }} file {{ path }} lineMatches {{ preview lineNumber }} }} }} }} }} }}","variables":null}}'

        response = post(self.sourcegraph_api, data=data_sdn, headers=headers)
        return response.json()

    def process_data(self, data: dict, tla_name: str) -> list:
        """
        Processes the data to extract the repo names using the given TLA.
        """
        tlas_using_target = []
        for result in data['data']['search']['results']['results']:
            for line_match in result['lineMatches']:
                if f'target: tla_{tla_name}' in line_match['preview']:
                    tlas_using_target.append(result['repository']['name'].split('/')[-1])
        return tlas_using_target
