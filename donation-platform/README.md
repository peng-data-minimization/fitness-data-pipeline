# Fitness Data Donation Platform

A simple gunicorn flask app which allows athletes to donate their fitness data.

## How does work?

All personal fitness activity data is being donated. It can be choosen whether only public or also private activities are donated.

Currently supported fitness apps & platforms:
* Strava
* Garmin (currently `user:password` only)
* fitfile upload

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

### Kubernetes
The app can be deployed on Kubernetes with kubectl and the [deployment.yml](../deployment.yml). For more details see the Fitness Data Pipeline [README](../README.md).

### Heroku
The app can also be deployed standalone on Heroku. By default, the data donation feature and pipeline data minimization feature are not co-deployed or otherwise integrated.

1. Project structure: Heroku requires the Pipefile and a Heroku deployment specific Procfile exist in the project root. Therefore, as a workaround create a new git repo.
    ```
    $ cd donation-platform
    $ git init .
    $ git remote add heroku https://git.heroku.com/peng-data-minimization.git
    $ git add .
    $ git commit -m 'Initial heroku commit'
    ```

2. Deploy the app and scale the web worker as needed
    ```
    $ heroku config:set STRAVA_CLIENT_SECRET=<client-secret>
    $ heroku config:set STRAVA_CLIENT_ID=<client-id>
    $ git push heroku master
    $ heroku ps:scale web=1
    ```

3. Open the website and check the logs
    ```
    $ heroku open
    $ heroku logs --tail
    ```

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
$ docker exec $(docker ps -aqf "name=fitness-data-pipeline_kafka_1") /bin/bash -c "/opt/kafka_*/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic anon --from-beginning" # verify that messages have arrived
```
