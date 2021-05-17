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

client_id = 'YOUR CLIENT_ID HERE'
secret = 'YOUR SECRETO HERE'

service = OAuth2Service(
    client_id=client_id,  # your App ID from https://wakatime.com/apps
    client_secret=secret,  # your App Secret from https://wakatime.com/apps
    name='wakatime',
    authorize_url='https://wakatime.com/oauth/authorize',
    access_token_url='https://wakatime.com/oauth/token',
    base_url='https://wakatime.com/api/v1/')

redirect_uri = 'https://wakatime.com/oauth/test'
state = hashlib.sha1(os.urandom(40)).hexdigest()
params = {'scope': 'email,read_stats,read_logged_time',
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
stats = session.get('users/current/stats/last_7_days?writes_only=true')
json_format = json.loads(stats.text)["data"]
today_str = str(datetime.now().date())

df_records = pd.read_csv('records.csv')
for editor in json_format['editors']:
    editor_name = editor['name']
    editor_time = editor['total_seconds']
    row = {'fecha': today_str, 'tipo': 'editor', 'nombre': editor_name, 'tiempo': editor_time}
    df_records = df_records.append(row, ignore_index=True)
for language in json_format['languages']:
    language_name = language['name']
    language_time = language['total_seconds']
    row = {'fecha': today_str, 'tipo': 'language', 'nombre': language_name, 'tiempo': language_time}
    df_records = df_records.append(row, ignore_index=True)
for project in json_format['projects']:
    project_name = project['name']
    project_time = project['total_seconds']
    row = {'fecha': today_str, 'tipo': 'project', 'nombre': project_name, 'tiempo': project_time}
    df_records = df_records.append(row, ignore_index=True)
df_records.to_csv('records.csv', index=False)

# print(json.dumps(json_format, indent=4))
