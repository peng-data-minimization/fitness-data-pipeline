import json
import requests
import os
from utils import get_logger, get_base_path
from extractor import ActivityExtractor, ActivityExtractorException

logger = get_logger()

class StravaActivityExtractor(ActivityExtractor):
    PROVIDER_NAME = 'strava'

    def __init__(self, creds=None):
        self.access_token = creds.get("token", _get_access_token())
        if not self.access_token:
            raise ActivityExtractorException('Authorization not possible due to missing access token request parameter.')

        super(StravaActivityExtractor, self).__init__()

    def get_activity_ids(self, activities):
        return [activity['id'] for activity in activities]

    def get_activity(self, id, include_all_efforts=False):
        # include all segments efforts (optional)
        params = {'include_all_efforts': include_all_efforts}
        activity = self._get_strava_request(f'/activities/{id}', params)
        return activity

    def get_activities(self):
        params = {'per_page': 200, 'page': 1}
        activities = self._get_strava_request('/athlete/activities', params)
        return activities

    def get_detailed_activities(self, include_all_efforts=False):
        activities = []
        for activity in self.get_activities():
            activities.append(self.get_activity(activity['id'], include_all_efforts))
        return activities

    def persist_activity(self, id, include_all_efforts=False):
        activity = self.get_activity(id, include_all_efforts)
        file_path = os.path.join(get_base_path(), 'strava', 'data', f'activity-{id}.json')
        with open(file_path, 'w') as f:
            json.dump(activity, f, indent=4, sort_keys=True)

    def persist_activities(self, include_all_efforts=False):
        for activity in self.get_activities():
            self.persist_activity(activity['id'], include_all_efforts)

    def _get_strava_request(self, path, params=None):
        logger.info(self.access_token)
        header = {'Authorization': 'Bearer ' + self.access_token}
        url = 'https://www.strava.com/api/v3/' + path
        r = requests.get(url=url, headers=header, params=params)
        if r.status_code != 200:
            raise ActivityExtractorException(f'Request failed.\n\turl: {r.url}\n\tstatus_code: {r.status_code}\n\tresponse: {r.text}')

        return r.json()

def _get_access_token():
    token_path = os.path.join(get_base_path(), 'strava', 'strava-token.json')
    with open(token_path, 'r') as file:
        creds = json.load(file)
        return creds['access_token']