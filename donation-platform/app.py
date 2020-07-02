import grequests
from flask import Flask, render_template, request, make_response, jsonify
from utils import strava_connector, kafkaproducer_connector, get_logger, get_access_token
import json
import uuid
import os
import re
import requests


app = Flask(__name__)
logger = get_logger()


@app.route('/')
def home():
    response = make_response(render_template('home.html'))

    if not request.cookies.get('session_id'):
        session_id = str(uuid.uuid4())
        response.set_cookie('session_id', session_id)

    return response


@app.route('/get_bot_response')
def get_bot_response():
    user_text = request.args.get('msg')
    state = request.args.get('state')

    if state:
        state = json.loads(state)
    else:
        state = {'mode': 'main_menu'}

    if (state and state['mode'] == 'concerns') or (re.search('concerns', user_text)):
        return {'response': "No really, don't worry, our donation platform is really completely safe.",
                'state': json.dumps({'mode': 'main_menu'})}
    else:
        return {'response': "Don't worry, our donation platform is completely safe.",
                'state': json.dumps({'mode': 'main_menu'})}


@app.route('/authorize/strava')
def authorize_strava():
    return strava_connector.authorize()


@app.route('/strava', methods=['GET'])
def strava():
    return render_template('service.html', service_description='STRAVA')


@app.route("/exchange_token")
def exchange_token():
    code = request.args.get('code')
    token = strava_connector.get_token(code)
    kafkaproducer_connector.donate_activity_data(token)
    return render_template('service.html', service_description='STRAVA')


@app.route("/donate-again")
def donate():
    token = get_access_token('strava')
    kafkaproducer_connector.donate_activity_data(token)
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(port=7777, host='0.0.0.0')
