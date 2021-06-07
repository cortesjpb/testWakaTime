#!/usr/bin/env python

import hashlib
import os
import sys
import json
from rauth import OAuth2Service
from datetime import datetime
import pandas as pd

if sys.version_info[0] == 3:
    raw_input = input

client_id = ''
secret = ''

service = OAuth2Service(
    client_id=client_id,  # your App ID from https://wakatime.com/apps
    client_secret=secret,  # your App Secret from https://wakatime.com/apps
    name='wakatime',
    authorize_url='https://wakatime.com/oauth/authorize',
    access_token_url='https://wakatime.com/oauth/token',
    base_url='https://wakatime.com/api/v1/')

redirect_uri = 'https://wakatime.com/oauth/test'
state = hashlib.sha1(os.urandom(40)).hexdigest()
params = {'scope': 'email,read_stats,read_logged_time,write_logged_time',
          'response_type': 'code',
          'state': state,
          'redirect_uri': redirect_uri}

url = service.get_authorize_url(**params)

print('**** Visit this url in your browser ****'.format(url=url))
print('*' * 80)
print(url)
print('*' * 80)
print('**** After clicking Authorize, paste code here and press Enter ****')
code = raw_input('Enter code from url: ')

# Make sure returned state has not changed for security reasons, and exchange
# code for an Access Token.
headers = {'Accept': 'application/x-www-form-urlencoded'}
print('Getting an access token...')
session = service.get_auth_session(headers=headers,
                                   data={'code': code,
                                         'grant_type': 'authorization_code',
                                         'redirect_uri': redirect_uri})

print('Getting current user from API...')
user = session.get('users/current').json()
print('Authenticated via OAuth as {0}'.format(user['data']['email']))
print("Getting user's coding stats from API...")
# stats = session.get('users/current/stats/last_7_days?writes_only=true')
projects_response = session.get('users/current/projects')
projects_data = json.loads(projects_response.text)["data"]
project_names = [project['name'] for project in projects_data]


with open('time_track.csv', 'a') as time_track:
    for project in project_names:
        project_response = session.get(f'users/current/summaries?project={project}&range=last+7+days+from+yesterday')
        project_details = json.loads(project_response.text)["data"]
        for day in project_details:
            date = day['range']['date']
            if len(day['editors']):
                editor = day['editors'][0]['name']
                for entity in day['entities']:
                    file_name = entity['name']
                    file_extension = file_name.split('.')[-1]
                    total_seconds = str(entity['total_seconds'])
                    time_track.write(','.join([date, editor, project, file_name, file_extension, total_seconds]) + '\n')

# print(json.dumps(project_details, indent=4))


# today_str = str(datetime.now().date())

