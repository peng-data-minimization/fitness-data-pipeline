import logging
import requests
import os
import json
from flask import redirect
import urllib

STRAVA_SCOPES = 'activity:read,activity:read_all'
logger = logging.getLogger()


def authorize():
    return redirect(location=authorize_url(), code=302)


def authorize_url():
    base_url = 'https://www.strava.com/oauth/authorize'
    params = {
        'client_id': os.getenv('STRAVA_CLIENT_ID'),
        'response_type': 'code',
        "redirect_uri": get_callback_url(),
        'scope': STRAVA_SCOPES,
        "approval_prompt": "force"
    }
    encoded_params = urllib.parse.urlencode(params)
    return base_url + '?' + encoded_params


def get_callback_url():
    app_domain = os.getenv('APP_DOMAIN_NAME', 'localhost')
    return 'http://' + app_domain + ':7777/exchange_token'


def get_token(code):
    params = {
        "client_id": os.getenv('STRAVA_CLIENT_ID'),
        "client_secret": os.getenv('STRAVA_CLIENT_SECRET'),
        "code": code,
        "grant_type": "authorization_code"
    }
    response = requests.post("https://www.strava.com/oauth/token", params)
    if response.status_code != 200:
        logger.error(f'Retrieving access token failed. {response.url} - {response.text}')
        return

    token_data = response.json()
    with open('strava-token.json', 'w') as f:
       json.dump(token_data, f, indent=4, sort_keys=True)

    return token_data.get('access_token')