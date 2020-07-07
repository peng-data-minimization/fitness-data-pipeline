import requests
import os
from utils import get_logger
import urllib

logger = get_logger()


def donate_activity_data(params, file=None):
    if file:
        files = {'file': (file.filename, file.stream, file.mimetype)}
    else:
        files = None
    if params:
        encoded_params = urllib.parse.urlencode(params)
    else:
        encoded_params = ''
    producer_domain = os.getenv('PRODUCER_DOMAIN_NAME', 'localhost')
    url = 'http://' + producer_domain + ':7778/donate-activities?' + encoded_params
    logger.debug(f'Calling kafka-producer: {url}')
    # grequests.get(url, hooks={'response': handle_response})
    response = requests.get(url, files=files)
    if response.status_code == 200:
        logger.debug(f'Donating activity data was successful. {response.url}')
    else:
        logger.error(f'Donating activity data failed. {response.url} - {response.status_code} - {response.text}')


def handle_response(response, **kwargs):
    if response.status_code == 200:
        logger.debug(f'Donating activity data was successful. {response.url}')
    else:
        logger.error(f'Donating activity data failed. {response.url} - {response.text} - {kwargs}')
    response.close()
