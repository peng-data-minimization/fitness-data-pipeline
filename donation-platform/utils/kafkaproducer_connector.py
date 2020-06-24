# import grequests
import requests
import os
from utils import get_logger
import time
import urllib
logger = get_logger()


def donate_activity_data(access_token):
    params = {'token': access_token}
    encoded_params = urllib.parse.urlencode(params)
    producer_domain = os.getenv('PRODUCER_DOMAIN_NAME', 'localhost')
    url = 'http://' + producer_domain + ':7778/donate-activities?' + encoded_params
    logger.debug(f'Calling kafka-producer: {url}')
    # grequests.get(url, hooks={'response': handle_response})
    response = requests.get(url)
    if response.status_code == 200:
        logger.debug(f'Donating activity data was successful.')
    else:
        logger.error(f'Donating activity data failed.')


def handle_response(response, **kwargs):
    if response.status_code == 200:
        logger.debug(f'Donating activity data was successful. {response.url}')
    else:
        logger.error(f'Donating activity data failed. {response.url} - {response.text} - {kwargs}')
    response.close()