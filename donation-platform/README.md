# Fitness Data Donation Platform

A simple gunicorn flask app which allows athletes to donate their fitness data.

## How does work?

All personal fitness activity data is being donated. It can be choosen whether only public or also private activities are donated.

Currently supported fitness apps & platforms:
* Strava

## Usage

### GET `/authorize/<platform>`

Authorize the app to access and donate your fitness platform activities (e.g. Strava). Open in local browser:
```
open http://localhost:7777/authorize/strava
```
<img src="static/authorize-strava-example.png" alt="Strava Authorization" height="500" />

### GET `/donate-again`
Donate fitness data of previously authorized platform again.


## Deployment

The app is being deployed with Kubernetes as part of a Confluent Streaming Platform. For more details see the Fitness Data Pipeline [README](../README.md).

## Development

For local testing purposes, the flask app can be run by itself [1] or as part of a local, trimmed Kafka Pipeline [2]. Make sure `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` are set as env vars.

```
$ python donation-platform/app.py # Option 1

```

```
$ docker-compose up --build # Option 2
```

For Option 2, it can further be checked if the messages were send and processed successfully.
```
$ curl -X GET http://localhost:7778/generate-data/start # testing kafka-producer
$ docker exec $(docker ps -aqf "name=fitness-data_kafka-server_1") /bin/bash -c "/opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic anon --from-beginning" # verify that messages have arrived
```
