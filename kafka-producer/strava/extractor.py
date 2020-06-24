
import os
import json
import requests
import os
from utils import get_logger, get_base_path

logger = get_logger()

def get_access_token():
    token_path = os.path.join(get_base_path(), 'strava/strava-token.json')
    with open(token_path, 'r') as file:
        creds = json.load(file)
        return creds['access_token']

def get_strava_activites():
    logger.debug("Getting Strava activities...")
    params = {'per_page': 200, 'page': 1}
    activities = _get_strava_request('/athlete/activities', params)
    return activities

def get_strava_activity(id, include_all_efforts=False):
     # include all segments efforts (optional)
    params = {'include_all_efforts': include_all_efforts}
    activity = _get_strava_request(f'/activities/{id}', params)
    return activity

def persist_strava_activity(id, include_all_efforts=False):
    activity = get_strava_activity(id, include_all_efforts)
    file_path = os.path.join(get_base_path(), f'strava/data/activity-{id}.json')
    with open(file_path, 'w') as f:
       json.dump(activity, f, indent=4, sort_keys=True)

def _get_strava_request(path, params=None):
    access_token = os.getenv('STRAVA_ACCESS_TOKEN', get_access_token())
    header = {'Authorization': 'Bearer ' + access_token}
    url = 'https://www.strava.com/api/v3/' + path
    r = requests.get(url=url, headers=header, params=params)
    if r.status_code != 200:
        logger.warn(f'Request failed.\n\turl: {r.url}\n\tstatus_code: {r.status_code}\n\tresponse: {r.text}')
        return
    return r.json()

# print(get_strava_activity(3483107731))
# data_dir = os.path.join(get_base_path(), 'data')cd
# with open(os.path.join(data_dir, 'activities'), 'r') as f:
#     for activity_id in f:
#         print(activity_id)
#         print(get_strava_activity(activity_id))
# print(get_strava_activites())