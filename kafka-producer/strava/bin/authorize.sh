#!/usr/bin/env bash

[ -z "$STRAVA_CLIENT_ID" ] && read -p "Please enter STRAVA_CLIENT_ID: " STRAVA_CLIENT_ID
[ -z "$STRAVA_CLIENT_SECRET" ] && read -p "Please enter STRAVA_CLIENT_SECRET: " STRAVA_CLIENT_SECRET

open "http://www.strava.com/oauth/authorize?\
client_id=$STRAVA_CLIENT_ID&\
response_type=code&\
redirect_uri=http://localhost/exchange_token&\
approval_prompt=force&\
scope=activity:read,activity:read_all"

# token scopes:
# - read (default)
# - activity:read (allows accessing activities)
# - activity:read_all (allows accessing private activities)

read -p "Please enter the 'code' url param from the redirect: " STRAVA_CODE

curl -X POST https://www.strava.com/oauth/token \
	-F client_id=$STRAVA_CLIENT_ID \
	-F client_secret=$STRAVA_CLIENT_SECRET \
	-F code=$STRAVA_CODE \
	-F grant_type=authorization_code \
    2> /dev/null | jq . | tee strava/strava-token.json