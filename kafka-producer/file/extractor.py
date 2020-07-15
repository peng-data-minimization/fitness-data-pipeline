from extractor import ActivityExtractor
from fitparse import FitFile
import uuid
import os
from utils import get_base_path
import json


class FitFileActivityExtractor(ActivityExtractor):
    PROVIDER_NAME = 'fitfile'

    def __init__(self, file_stream):
        self.fitfile = FitFile(file_stream)
        self.activity_id = str(uuid.uuid4())

    def get_activity(self, id):
        raise NotImplementedError("One fit file always contains data for one activity only")

    def get_activities(self):
        data = []
        for index, record in enumerate(self.fitfile.get_messages('record')):
            if index > 196: # for the demo, we need to cut off the beginning of the file
                record_dict = {metric.name: metric.value if metric.name != "timestamp" else metric.raw_value
                               for metric in record}
                record_dict.update({
                    'activityId': self.activity_id,
                    'type': 'fitfile_upload',
                    "position_lat": self.semicircles_to_degrees(record_dict["position_lat"]),
                    "position_long": self.semicircles_to_degrees(record_dict["position_long"])})
                data.append(record_dict)
        return data

    def persist_activity(self, id):
        raise NotImplementedError("One fit file always contains data for one activity only")

    def persist_activities(self):
        file_path = os.path.join(get_base_path(), 'fitfile', 'data', f'activity-{self.activity_id}.json')
        activities = self.get_activities()
        with open(file_path, 'w') as f:
            json.dump(activities, f, indent=4, sort_keys=True)

    def get_activity_ids(self, activities):
        return [self.activity_id]

    def semicircles_to_degrees(self, semicircles):
        return semicircles * 180 / 2 ** 31
