#!/usr/bin/env python3

import os
import sys
import argparse
from bs4 import BeautifulSoup
import multiprocessing
import logging
import requests
from string import ascii_lowercase, ascii_uppercase
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

data_dir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))
    ), 'strava', 'data')

if not os.path.isdir(data_dir):
    os.mkdir(data_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] {%(funcName)s} %(levelname)s - %(message)s',
)
log = logging.getLogger()


def init_session(args):
    session = requests.session()

    r = session.get('https://www.strava.com/login')
    page = BeautifulSoup(r.text, 'html.parser')
    token = page.head.find(
        'meta', attrs={'name': 'csrf-token'}).attrs['content']
    log.debug(token)

    r = session.post(
        url = 'https://www.strava.com/session',
        data = {
            'utf-8': '✓',
            'plan': None,
            'email': args.email,
            'password': args.passwd,
            'authenticity_token': token
        })

    retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
    session.mount('https://www.strava.com/athletes', HTTPAdapter(max_retries=retries))
    session.mount('https://www.strava.com/athletes/search', HTTPAdapter(max_retries=retries))

    log.debug(requests.utils.dict_from_cookiejar(session.cookies))
    return session

def get_athletes(session, letters):
    athlete_ids = []
    # Strava will not get result above page 50
    for page in range(5):
        if page != 0:
            real_page = '&page=%s' % (page + 1)
        else:
            real_page = ''

        r = session.get(
            url = 'https://www.strava.com/athletes/search',
            params = {
                'utf8': '✓',
                'text': '%s%s' % (letters, real_page)
            })
        if r.status_code != 200:
            log.error('Failure')
            break

        page = BeautifulSoup(r.text, 'html.parser')
        for el in page.body.select('[data-athlete-id]'):
            if el.attrs['data-requires-approval'] == 'false':
                athlete_ids.append(el.attrs['data-athlete-id'])
    return athlete_ids

def get_activities(session, athlete):
    activity_ids = []
    for year in ['2018', '2019', '2020']:
        for m in range(12):
            month = '{0:02d}'.format(m + 1)

            r = session.get(
                url = f'https://www.strava.com/athletes/{athlete}',
                params = {
                    'chart_type': 'miles',
                    'interval_type': 'month',
                    'interval': '%s%s' % (year, month),
                    'year_offset': 0
                })

            if r.status_code != 200:
                log.error('Failure')
                break

            page = BeautifulSoup(r.text, 'html.parser')
            interval_rides = page.find('div', {'id': 'interval-rides'})
            activities = interval_rides.select('.feed.feed-moby .activity.entity-details.feed-entry')

            for activity in activities:
                div_id = activity.attrs['id']
                if div_id.startswith('Activity-'):
                    activity_id = div_id[9:]
                    activity_ids.append(activity_id)
    return activity_ids


def get_activities_worker(q, args):
    session = init_session(args)
    while True:
        athlete_id = q.get()
        activity_ids = get_activities(session, athlete_id)
        with open(os.path.join(data_dir, 'activities'), 'a') as outfile:
            outfile.write('\n'.join(activity_ids).append('\n'))


def get_athletes_worker(q, args):
    session = init_session(args)
    while True:
        search_str = q.get()
        athlete_ids = get_athletes(session, search_str)
        with open(os.path.join(data_dir, 'athletes'), 'a') as outfile:
            outfile.write('\n'.join(athlete_ids).append('\n'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Request strava for random athletes data')
    parser.add_argument('type', nargs='?', help='Strava entity type [activities, athletes]')
    parser.add_argument('email', nargs='?', help='Strava account email')
    parser.add_argument('passwd', nargs='?', help='Strava account password')
    args = parser.parse_args()

    if not args.email or not args.passwd:
        log.error('Email or password not set')
        parser.print_help()
        sys.exit(1)

    q = multiprocessing.Queue(maxsize=200)

    ps = []
    for i in range(16):
        if args.type == 'activities':
            p = multiprocessing.Process(target=get_activities_worker, args=(q, args))
        else:
            p = multiprocessing.Process(target=get_athletes_worker, args=(q, args))
        p.start()
        ps.append(p)

    if args.type == 'activities':
        with open(os.path.join(data_dir, 'athletes'), 'r') as f:
            for athlete in f:
                q.put(athlete)
    else:
        for one in ascii_lowercase + ascii_uppercase:
            if one in ['a', 'b', 'c', 'd']:
                continue
            for two in ascii_lowercase + ascii_uppercase:
                q.put('%s%s' % (one, two))

    for p in ps:
        p.join()