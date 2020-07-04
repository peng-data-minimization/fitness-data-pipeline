import os
import json
import random
import secrets
from datetime import datetime, timedelta
from utils import get_logger, get_base_path
from generator import ActivityGenerator
from faker import Faker
logger = get_logger()
faker = Faker()
TYPES = ['Ride']
DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
MAX_RETRIES = 10


class StravaActivityGenerator(ActivityGenerator):
    PROVIDER_NAME = 'strava'

    # Faking data for Strava API v3 /activities/{id} (variances of example-activity.json)
    # IMPORTANT: this function does not anonymize activities,
    # it just randomly changes values while trying to maintain most semantic coherences
    def generate_dummy_activity(self):
        file_path = os.path.join(get_base_path(), 'strava/example-activity.json')
        for _ in range(MAX_RETRIES):
            with open(file_path, 'r') as file:
                activity = json.load(file)

            fake_activity(activity)

            for segment in activity['segment_efforts']:
                fake_segment(activity, segment)

            for lap in activity['laps']:
                fake_lap(activity, lap)

            for split in activity['splits_metric']:
                fake_split_metric(activity, split)

            try:
                verify_data_integrity(activity)
            except AssertionError:
                logger.info('Generated activity data not consistent. Trying again...')
                continue
            return activity
        else:
            logger.warning(f'Generating consistent activity data failed {MAX_RETRIES} times. Aborting and using inconsistent values')


def verify_data_integrity(activity):
    verify_max_values(activity)
    verify_avg_values(activity)
    verify_perturbed_values(activity)


def fake_activity(activity):
    activity['id'] = faker.random_int(1, 100000000)
    activity['athlete']['id'] = faker.random_int(1, 100000000)
    activity['embed_token'] = secrets.token_hex(25)
    activity['external_id'] = secrets.token_hex(25)
    activity['achievement_count'] = faker.random_int(0, 25)
    activity['upload_id'] = faker.random_int(1, 100000000)
    activity['upload_id_str'] = str(activity['upload_id'])
    activity['map'] = {}
    activity['type'] = random.choice(TYPES)
    activity['start_date'] = faker.date_time_this_decade().strftime(DATE_FORMAT)
    activity['start_date_local'] = activity['start_date']
    activity['elapsed_time'] = faker.random_int(1, 50000)
    activity['moving_time'] = activity['elapsed_time'] * rf(min=0.9, max=1.0, decimals=5)
    activity['average_heartrate'] = rf(min=60, max=190)
    activity['max_heartrate'] = rf(min=activity['average_heartrate'], max=190)
    activity['average_speed'] = rf(12.0, decimals=3)
    activity['max_speed'] = rf(min=activity['average_speed'], max=12.0, decimals=3)
    activity['calories'] = rf(5000.0)
    activity['distance'] = rf(250000.0)
    activity['elev_low'] = rf(1000)
    activity['elev_high'] = activity['elev_low'] + rf(1000)
    activity['total_elevation_gain'] = round((activity['elev_high'] - activity['elev_low']) * rf(min=1.0, max=10.0, decimals=5), 1)
    activity['start_latitude'] = round(float(faker.latitude()), 6)
    activity['start_longitude'] = round(float(faker.longitude()), 6)
    activity['start_latlng'] = [activity['start_latitude'], activity['start_longitude']]
    activity['end_latlng'] = [round(float(faker.latitude()), 6), round(float(faker.longitude()), 6)]
    activity['utc_offset'] = 0.0
    activity['timezone'] = 'Africa/Accra [GMT 00:00]'
    activity['name'] = 'Fahrt am Nachmittag'


def fake_segment(activity, segment):
    segment['id'] = faker.random_int(1, 100000000)
    segment['activity']['id'] = activity['id']
    segment['athlete']['id'] = activity['athlete']['id']
    segment['max_heartrate'] = rf(min=activity['average_heartrate'], max=activity['max_heartrate'])
    segment['average_heartrate'] = rf(min=60, max=segment['max_heartrate'])
    segment['elapsed_time'] = segment['distance'] / activity['average_speed']
    segment['moving_time'] = segment['elapsed_time'] * rf(min=0.9, max=1.0, decimals=5)
    segment['start_date'] = get_lap_date(activity)
    segment['start_date_local'] = segment['start_date']
    # WARNING segment['segment']['city'] segment['segment']['start_latitude'] etc. are not changed


def fake_lap(activity, lap):
    num_laps = len(activity['laps'])
    lap['activity']['id'] = activity['id']
    lap['athlete']['id'] = activity['athlete']['id']
    lap['max_heartrate'] = rf(min=activity['average_heartrate'], max=activity['max_heartrate'])
    lap['average_heartrate'] = rf(min=60, max=lap['max_heartrate'])
    lap['max_speed'] = rf(min=activity['average_speed'], max=activity['max_speed'], decimals=3)
    lap['average_speed'] = rf(lap['max_speed'], decimals=3)
    lap['distance'] = round(activity['distance'] / num_laps, 1)
    lap['elapsed_time'] = round(activity['elapsed_time'] / num_laps)
    lap['moving_time'] = round(lap['elapsed_time'] * rf(min=0.9, max=1.0, decimals=5))
    lap['calories'] = round(activity['calories'] / num_laps, 1)
    lap['start_date'] = get_lap_date(activity)
    lap['start_date_local'] = lap['start_date']
    lap['total_elevation_gain'] = round(activity['total_elevation_gain'] / num_laps, 1)


def fake_split_metric(activity, split):
    num_splits = len(activity['splits_metric'])
    split['average_heartrate'] = round(activity['average_heartrate'] * rf(min=0.6, max=1.4, decimals=5), 14)
    split['average_speed'] = round(activity['average_speed'] * rf(min=0.33, max=3.0, decimals=5), 2)
    split['elapsed_time'] = round(activity['elapsed_time'] / num_splits * rf(min=0.33, max=3.0, decimals=5), 2)
    split['moving_time'] = round(split['elapsed_time'] * rf(min=0.9, max=1.0, decimals=5))
    split['distance'] = round(split['average_speed'] * split['moving_time'], 1)
    split['elevation_difference'] = round(activity['total_elevation_gain'] / num_splits * rf(min=0, max=4.0, decimals=5) * random.choice([-1, 1]), 1)


def get_lap_date(activity):
    activity_start_date = datetime.strptime(activity['start_date'], DATE_FORMAT)
    activity_end_date = activity_start_date + timedelta(0, activity['elapsed_time'])
    lap_start_date = faker.date_between_dates(date_start=activity_start_date, date_end=activity_end_date)
    return lap_start_date.strftime(DATE_FORMAT)


# generate random floats
def rf(max, min=0.0, decimals=1):
    return round(random.uniform(min, max), decimals)


# perturbed split, lap or segment values shall be in reasonable interval of overall values
def verify_perturbed_values(activity):

    # should be mostly inside interval
    assert activity['total_elevation_gain'] * 0.9 < sum(split['elevation_difference'] for split in activity['splits_metric'] if split['elevation_difference'] > 0 ) < activity['total_elevation_gain'] * 1.1


# averaged values should be exactly the same except for rounding errors
def verify_avg_values(activity):
    assert round(activity['total_elevation_gain'], -1) == round(sum(lap['total_elevation_gain'] for lap in activity['laps'] if lap['total_elevation_gain'] > 0 ), -1)

    if len(activity['segment_efforts']) > 0:
        # estimated segment elapsed_time and fixed segment distance should coresspond to overall average speed
        assert round(sum(segment['distance'] for segment in activity['segment_efforts']) / sum(segment['elapsed_time'] for segment in activity['segment_efforts']), 3) == activity['average_speed']

    # sum(lap['average_heartrate'] for lap in activity['laps']) / len(activity['laps'])
    # assert sum(lap['average_speed'] for lap in activity['laps']) / len(activity['laps'])


# segment or lap max values cannot be higher than overall max values
def verify_max_values(activity):
    assert not any(lap['max_speed'] > activity['max_speed'] for lap in activity['laps'])
    assert not any(lap['max_heartrate'] > activity['max_heartrate'] for lap in activity['laps'])
    assert not any(segment['max_heartrate'] > activity['max_heartrate'] for segment in activity['segment_efforts'])