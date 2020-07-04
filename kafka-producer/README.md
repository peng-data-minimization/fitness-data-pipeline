# Kafka Producer for Fitness Data

A simple python Kafka producer that collects donated fitness data and scrapes publicly available data.

Currently supported fitness apps & platforms:
* Strava
* Garmin (currently `user:password` only)

## Usage

### GET `/donate-activities`
* `?app=strava&token=<access-token>`
* `?app=garmin&username=<username>&password=<password>`
Donates all personal fitness activity data visible with given `access-token` / `username:password`. The endpoint is automically being called after authorizing the donation platform to access ones fitness data (e.g. `/authorize/strava`).

### GET `/generate-data/{start,stop}?app=<garmin/strava/all>&interval=<seconds>`
Starts / stops continuously producing exemplary fitness data. Each second an activity is send to the ingestion Kafka topic. All parameters are optional. The default interval is 1 second.


## Deployment

The producer is being deployed with Kubernetes as part of a Confluent Streaming Platform. For more details see the Fitness Data Pipeline [README](../README.md).


## Development

To build and test locally:
```
$ docker-compose up --build
```

Start sending data:
```
$ curl -X GET http://localhost:7778/generate-data/start # testing kafka-producer
```

Verify that data was send and processed successfully:
```
$ docker exec $(docker ps -aqf "name=fitness-data-pipeline_kafka_1") /bin/bash -c "/opt/kafka_*/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic anon --from-beginning"
```