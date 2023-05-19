'''
    Fill in the following yourself (lines 145-148):
    - email = Ubisoft account full email
    - password = Ubisoft account password
    - reason = Basic intended usage/app
    - audience

    audience is preset to NadeoLiveServices but you can change it if you want to access a different part of the TM API
    Read https://webservices.openplanet.dev/auth for more information.

    If this script completes successfully, you will have the API token saved in level_2_tokens.txt in this scripts folder.

    I did not make the script accept input parameters on purpose, as I do not want to encourage people blindly inputting their emails and passwords without checking the code for any malicious usages beforehand.
'''

import sys
import json
from base64 import b64encode
import requests


def encode_user(user_email: str, user_password: str) -> str:
    encoded_user_str = b64encode(
        f'{user_email}:{user_password}'.encode('utf-8')).decode('ascii')
    return f'Basic {encoded_user_str}'


def get_ubisoft_level_0_token(authorization_user: str, user_email: str, user_agent_reason: str):
    # Fix so that only the token gets returned.
    print('Obtaining level 0 token...')

    level_0_request_url = 'https://public-ubiservices.ubi.com/v3/profiles/sessions'
    headers = {'Authorization': authorization_user,
               'Ubi-AppId': '86263886-327a-4328-ac69-527f0d20a237',
               'Ubi-RequestedPlatformType': 'uplay',
               'Content-Type': 'application/json',
               'User-Agent': f'{user_agent_reason} / {user_email}'}

    response = requests.post(level_0_request_url, headers=headers, timeout=5)

    if response.status_code == 200:
        print('Level 0 token obtained.')
        ticket = response.json()['ticket']
        try:
            with open('level_0_token_aka_ticket.txt', 'w', encoding='utf-8') as file:
                print('Saving level 0 token to level_0_token_aka_ticket.txt')
                json.dump(response.json(), file, indent=4)
                print('Saved level 0 token to level_0_token_aka_ticket.txt')
            file.close()

            return ticket
        except IOError as io_exception:
            print(
                f'I/O exception {io_exception.errno}: {io_exception.strerror}')

    else:
        print('Status code:', response.status_code)
        print('Exiting script, incorrect response.')
        sys.exit()

    return ""


def get_ubisoft_level_1_token(token: str) -> str:
    # Fix so that only the access token gets returned.
    print('Obtaining level 1 tokens...')
    level_1_request_url = 'https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices'
    auth_string = 'ubi_v1 t=' + token
    headers = {'Content-Type': 'application/json',
               'Authorization': auth_string}

    response = requests.post(level_1_request_url, headers=headers, timeout=5)

    if response.status_code == 200:
        print('Level 1 access and refresh tokens obtained.')
        level_1_access_token = response.json()['accessToken']
        try:
            with open('core_api_token.txt', 'w', encoding='utf-8') as file:
                print('Saving level 1 tokens to core_api_token.txt')
                json.dump(response.json(), file, indent=4)
                print('Saved level 1 tokens to core_api_token.txt')
            file.close()

            return level_1_access_token
        except IOError as exception:
            print(f'I/O exception {exception.errno}: {exception.strerror}')
    else:
        print('Error! Status code:', response.status_code)
        print('Exiting script, incorrect response.')
        sys.exit()

    return ""


def get_ubisoft_level_2_token(level_1_token: str, target_audience: str) -> str:
    # Fix so that only the access token gets returned.
    print('Obtaining level 2 tokens for the Live API...')
    level_2_request_url = 'https://prod.trackmania.core.nadeo.online/v2/authentication/token/nadeoservices'
    auth_string = 'nadeo_v1 t=' + level_1_token
    header = {'Authorization': auth_string}
    body = {'audience': target_audience}

    response = requests.post(
        level_2_request_url, headers=header, json=body, timeout=5)

    if response.status_code == 200:
        print('Level 2 access and refresh tokens obtained.')
        level_2_access_token = response.json()['accessToken']
        try:
            with open('live_api_tokens.txt', 'w', encoding='utf-8') as file:
                print('Saving level 2 tokens to live_api_tokens.txt')
                json.dump(response.json(), file, indent=4)
                print('Saved level 2 tokens to live_api_tokens.txt')
            file.close()

            return level_2_access_token
        except IOError as exception:
            print(f'I/O exception {exception.errno}: {exception.strerror}')
    else:
        print('Error! Status code:', response.status_code)
        print('Exiting script, incorrect response.')
        sys.exit()

    return ""


def map_leaderboards_example_api_call(live_token: str):
    '''
        This is the example from the openplanet API documentation: https://webservices.openplanet.dev/live/leaderboards/top
    '''
    print('Testing the token with an API call')
    api_call_url = 'https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/Personal_Best/map/ZJw6_4CItmVlRMPgELl4Q37Utw2/top?onlyWorld=true&length=10&offset=50'
    header = {'Authorization': f'nadeo_v1 t={live_token}'}

    response = requests.get(api_call_url, headers=header, timeout=5)
    if response.status_code == 200:
        print('The token works!')
    else:
        print('Error! Status code:', response.status_code)
        print('Exiting script, incorrect response.')
        sys.exit()


if __name__ == "__main__":
    email = ''  # example: randomUser123@geemail.com
    password = ''
    reason = ''
    audience = 'NadeoLiveServices'  # other options: NadeoClubServices

    if not email or not password:
        print('ERROR: No email and/or password provided.')
        sys.exit()

    encoded_user = encode_user(email, password)
    level_0_token = get_ubisoft_level_0_token(encoded_user, email, reason)
    # level 1 token = core API token
    core_api_token = get_ubisoft_level_1_token(level_0_token)
    live_api_token = get_ubisoft_level_2_token(core_api_token, audience)

    # Now we check that the level 2 (live) token works using the example provided by the trackmania API:
    map_leaderboards_example_api_call(live_api_token)
    print('Check the file named live_api_tokens.txt for the Live API access token.')
    print('Check the file named core_api_token.txt for the Core API access token.')
