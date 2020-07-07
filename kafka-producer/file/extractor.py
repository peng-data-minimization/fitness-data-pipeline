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
        self.activity_id = uuid.uuid4()

    def get_activity(self, id):
        raise NotImplementedError("One fit file always contains data for one activity only")

    def get_activities(self):
        data = []
        for record in self.fitfile.get_messages('record'):
            record_dict = {metric.name: metric.value for metric in record}
            record_dict.update({'activity_id': self.activity_id})
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
