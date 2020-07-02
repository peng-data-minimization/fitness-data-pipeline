import os
from datetime import date
from utils import get_logger, get_base_path
from extractor import ActivityExtractor, ActivityExtractorException
from functools import wraps
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)


logger = get_logger()
today = date.today().isoformat()

def handle_garmin_exception(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except GarminConnectConnectionError as e:
            raise ActivityExtractorException(f'A Garmin Connect connection error occurred in {func.__name__}.', e)

        except GarminConnectTooManyRequestsError as e:
            raise ActivityExtractorException(f'Too many requests, the client was rate limited by Garmin Connect in {func.__name__}.', e)

        except GarminConnectAuthenticationError as e:
            raise ActivityExtractorException(f'A Garmin Connect authentication error occurred in {func.__name__}.', e)

        except Exception as e:  # pylint: disable=broad-except
            raise ActivityExtractorException(f'An unknown error occurred for Garmin Connect Client in {func.__name__}', e)

    return decorated

class GarminActivityExtractor(ActivityExtractor):
    PROVIDER_NAME = 'garmin'

    def __init__(self, creds):
        self.password = creds.get("password")
        self.user = creds.get("user")
        if not self.password or not self.user:
            raise ActivityExtractorException('Authorization not possible due to missing user or password request parameter.')

        super(GarminActivityExtractor, self).__init__()

    @handle_garmin_exception
    def get_client(self):
        '''
        Initialize Garmin client with credentials and login to Garmin Connect portal
        The library will try to relogin when session expires
        '''
        client = Garmin(self.user, self.password)
        client.login()
        return client

    def get_activity_ids(self, activities):
        return [activity['activityId'] for activity in activities]

    @handle_garmin_exception
    def get_profile_data(self):
        client = self.get_client()
        return client.get_full_name()

    @handle_garmin_exception
    def get_stats(self, date=today):
        client = self.get_client()
        return client.get_stats(date)

    @handle_garmin_exception
    def get_activity(self, id):
        client = self.get_client()
        batch = 50
        i = 0
        while True:
            activities = client.get_activities(batch*i, batch*(i+1))
            if len(activities) == 0:
                return
            activity = next((activity for activity in activities if str(activity['activityId']) == str(id)), None)
            if activity:
                return activity
            i += 1

    @handle_garmin_exception
    def get_activities(self, number=50):
        client = self.get_client()
        return client.get_activities(0, number)

    def persist_activities(self):
        for activity in self.get_activities():
            self.persist_activity(activity['activityId'])

    @handle_garmin_exception
    def persist_activity(self, activity_id, format='TCX'):
        client = self.get_client()

        if format == 'TCX':
            data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.TCX)
            output_file = f'{str(activity_id)}.tcx'
        elif format == 'GPX':
            data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.GPX)
            output_file = f'{str(activity_id)}.gpx'
        elif format == 'ZIP':
            data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.ORIGINAL)
            output_file = f'{str(activity_id)}.zip'
        else:
            raise ActivityExtractorException('Invalid or not supported activity format given. Supported fomarts are: TCX, GPX and ZIP')

        data_dir = os.path.join(get_base_path(), 'garmin', 'data')
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)

        with open(os.path.join(data_dir, output_file), 'wb') as fb:
            fb.write(data)

    @handle_garmin_exception
    def get_heart_rate_data(self, date=today):
        client = self.get_client()
        return client.get_heart_rates(date)