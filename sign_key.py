import os
import requests
VAULT_ADDR = os.getenv('VAULT_ADDR', 'https://vault-prd.prd.betfair')
VAULT_SIGN_PATH = '/v1/ssh/sign/signing_role'
TOKEN_LOCATION = '/home/centos/.vault_token'
sign_payload = {
    "public_key": "",
    "extension": {
        "permit-pty": ""
    },
    "ttl": "120h",
    "valid_principals": "provisioning,centos"
}
def write_key(signed_key, file_name):
    with open(file_name, 'w+') as f:
        f.write(signed_key)
    os.chmod(os.getcwd() + '/' + file_name, 0o600)
def get_public_key(token, key_name):
    """Get the public key used by go, in order to be signed by Vault"""
    headers = {'Content-Type': 'application/json', 'X-Vault-Token': token}
    response = requests.get(VAULT_ADDR + '/v1/tla_jas/common', headers=headers, verify=True)
    print(response.json())
    id_rsa = response.json()['data']['id_rsa']
    id_rsa_pub = response.json()['data']['id_rsa_pub']
    write_key(id_rsa, key_name)
    write_key(id_rsa_pub, key_name + '.pub')
    return id_rsa_pub
def get_power_token(token_location):
    """Get the power token from VAULT_TOKEN env var or from the default file /home/centos/.vault_token """
    token_file = os.path.expanduser(token_location)
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return f.read()
    return ''
def sign_key():
    key_name = 'id_rsa'
    power_token = get_power_token(TOKEN_LOCATION)
    public_key = get_public_key(power_token, key_name)
    headers = {'Content-Type': 'application/json', 'X-Vault-Token': power_token}
    sign_payload['public_key'] = public_key
    sign_response = requests.post(VAULT_ADDR + VAULT_SIGN_PATH, headers=headers,
                                  json=sign_payload, verify=True)
    if sign_response.status_code == 200:
        print('Public Key was signed by vault')
    else:
        print('There was an error signing the public key')
        raise Exception(
            "Public key was NOT signed - status code: {} - response text: {}".format(sign_response.status_code,
                                                                                     sign_response.text))
    data = sign_response.json()
    signed_key = data['data']['signed_key']
    write_key(signed_key, key_name + '-cert.pub')
    print('DONE! SSH your brains out')
def main():
    sign_key()
if __name__ == '__main__':
    main()

