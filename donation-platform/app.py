from gevent import monkey
monkey.patch_all()
from flask import Flask, render_template, request, make_response, jsonify, redirect, url_for, session, flash
from utils import strava_connector, kafkaproducer_connector, get_logger, get_access_token
import uuid
import secrets

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = secrets.token_urlsafe(16)
logger = get_logger()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/')
def home():
    response = make_response(render_template('index.html'))

    if not request.cookies.get('session_id'):
        session_id = str(uuid.uuid4())
        response.set_cookie('session_id', session_id)

    return response


@app.route('/authorize/strava')
def authorize_strava():
    session.clear()
    return strava_connector.authorize()


@app.route('/authorize/garmin')
def login_garmin():
    session.clear()
    return make_response(render_template('login.html'))


@app.route('/validate-login')
def validate_login():
    session['username'] = request.args.get('username', '')
    session['password'] = request.args.get('password', '')
    session.pop('token', None)
    session['app'] = 'GARMIN'
    return redirect(url_for('success'))


@app.route('/file/upload', methods=['POST', 'GET'])
def uploadfile():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            params = {'app': 'fitfile'}
            status = kafkaproducer_connector.donate_activity_data(params=params, file=file)
            return render_template('index.html', donation_status=status, service_description='.FIT file')
        else:
            flash('No selected file')
            return redirect(request.url)
    else:
        return make_response(render_template('upload.html'))


@app.route('/success')
def success():
    if 'token' in session:
        params = {'token': session['token']}
    elif 'username' in session and 'password' in session:
        params = {'username': session['username'], 'password': session['password']}

    params['app'] = session['app'].lower()
    status = kafkaproducer_connector.donate_activity_data(params)
    return render_template('index.html', donation_status=status, service_description=session['app'])


@app.route("/exchange_token")
def exchange_token():
    code = request.args.get('code')
    session['token'] = strava_connector.get_token(code)
    session['app'] = 'STRAVA'
    return redirect(url_for('success'))


@app.route("/donate-again")
def donate():
    app = request.args.get('app', 'strava')
    token = get_access_token(app)
    status = kafkaproducer_connector.donate_activity_data({'token': token, 'app': app})
    return jsonify(success=status)


if __name__ == '__main__':
    app.run(port=7777, host='0.0.0.0')
