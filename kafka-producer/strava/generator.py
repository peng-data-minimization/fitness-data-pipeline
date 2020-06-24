import os
import json
from utils import get_logger, get_base_path

logger = get_logger()

def generate_strava_dummy_activity():
    file_path = os.path.join(get_base_path(), 'strava/example-activity.json')
    with open(file_path, 'r') as file:
        return json.load(file)