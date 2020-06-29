from flask import Flask, request, jsonify
from utils import get_logger
from strava import extractor, generator
import producer
import json
import uuid
import time
import os
import requests
from threading import Thread

app = Flask(__name__)
logger = get_logger()

@app.route('/donate-activities')
def donate():
    os.environ['STRAVA_ACCESS_TOKEN'] = request.args.get('token')
    activities = extractor.get_strava_activites()
    producer.produce(activities)
    return jsonify(success=True)

@app.route('/generate-data/stop')
def stop_generation():
    os.environ['running_flag'] = 'stop'
    return jsonify(success=True)

@app.route('/generate-data/start')
def start_generation():
    os.environ['running_flag'] = 'running'
    t = Thread(target=generate_and_produce)
    t.daemon = True
    t.start()
    return jsonify(success=True)

def generate_and_produce():
    while os.getenv('running_flag') == 'running':
        activities = [generator.generate_strava_dummy_activity()]
        producer.produce(activities)
        time.sleep(1)

if __name__ == '__main__':
    app.run(port=7778, host='0.0.0.0')