from confluent_kafka import Producer
from utils import get_logger, json_default_converter
import json
import os

logger = get_logger()


def produce(activities):
    kafka_domain = os.getenv('KAFKA_DOMAIN_NAME', 'localhost')
    connection_string = f"{kafka_domain}:9092"

    logger.debug(f'Connecting to Kafka @ {connection_string} to send activities.')
    producer_conf = {'bootstrap.servers': connection_string}

    producer = Producer(producer_conf)

    logger.debug("Connected.")
    for activity in activities:
        logger.debug(
            f"Trying to send activity: id {activity.get('id', activity.get('activityId'))}, name {activity.get('name', activity.get('activityName'))}, type {activity.get('type', activity.get('typeKey'))}, ...")
        producer.produce('anon', serialize_message(activity))
    # block until all async messages are sent
    producer.flush()


def serialize_message(m):
    return json.dumps(m, default=json_default_converter).encode('ascii')


def on_send_success(record_metadata):
    logger.debug(
        f'Successfully send record - topic: {record_metadata.topic}, partition: {record_metadata.partition}, offset: {record_metadata.offset}')


def on_send_error(excp):
    logger.error('Failed to send record:', exc_info=excp)
