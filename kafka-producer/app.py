from flask import Flask, request, jsonify
from extractor import ActivityExtractor, ActivityExtractorException
from generator import ActivityGenerator
from utils import get_logger
from threading import Thread
import producer
import time
import os
import requests

app = Flask(__name__)
logger = get_logger()

@app.route('/donate-activities')
def donate():
    app = request.args.get('app', 'strava')
    try:
        extractor = ActivityExtractor.get_provider(provider_name=app, creds=request.args)
        activities = extractor.get_activities()
        donated_activity_ids = extractor.get_activity_ids(activities)
        logger.info(f'Extracted activities to be donated and processed: {donated_activity_ids}')
    except ActivityExtractorException as e:
        return jsonify(success=False, error=e.message), e.status

    try:
        producer.produce(activities)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

    return jsonify(success=True, donated_activities=donated_activity_ids)

@app.route('/generate-data/stop')
def stop_generation():
    app = request.args.get('app', 'all')
    apps = ActivityGenerator.get_provider_names() if app == 'all' else [app]
    for app in apps:
        os.environ[f'{app}_generation'] = 'stopped'
        logger.info(f"Following activity data generation processes are set to 'stopped': {apps}")
    return jsonify(success=True)

@app.route('/generate-data/start')
def start_generation():
    try:
        app = request.args.get('app', 'strava')
        intervall = request.args.get('intervall', 1)
        generator = ActivityGenerator.get_provider(provider_name=app)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 404

    os.environ[f'{app}_generation'] = 'running'
    t = Thread(target=generate_and_produce, args=[generator, intervall])
    t.daemon = True
    t.start()
    return jsonify(success=True)

def generate_and_produce(generator, intervall):
    provider = generator.PROVIDER_NAME
    while os.getenv(f'{provider}_generation') == 'running':
        activities = [generator.generate_dummy_activity()]
        try:
            producer.produce(activities)
        except Exception as e:
            logger.warning(str(e))
        time.sleep(intervall)

if __name__ == '__main__':
    app.run(port=7778, host='0.0.0.0')