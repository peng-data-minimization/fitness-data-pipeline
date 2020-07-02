from kafka import KafkaProducer
from utils import get_logger, get_base_path
from strava import generator
import json
import os

logger = get_logger()


def produce(activities):
    kafka_domain = os.getenv('KAFKA_DOMAIN_NAME', 'localhost')
    producer = KafkaProducer(bootstrap_servers=f'{kafka_domain}:9092', value_serializer=get_serializer(), retries=5)
    for activity in activities:
        logger.debug(f"Trying to send activity: id {activity.get('id', activity.get('activityId'))}, name {activity.get('name', activity.get('activityName'))}, type {activity.get('type', activity.get('typeKey'))}, ...")
        producer.send("anon", activity).add_callback(on_send_success).add_errback(on_send_error)

    # block until all async messages are sent
    producer.flush()


def get_serializer():
    return lambda m: json.dumps(m).encode('ascii')


def on_send_success(record_metadata):
    logger.debug(f'Successfully send record - topic: {record_metadata.topic}, partition: {record_metadata.partition}, offset: {record_metadata.offset}')


def on_send_error(excp):
    logger.error('Failed to send record:', exc_info=excp)

