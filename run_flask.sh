#!/usr/bin/env bash

# Go to https://console.cloud.google.com/apis/credentials/oauthclient
# and create credentials that you will use
export GOOGLE_CLIENT_ID=<INSERT_HERE>
export GOOGLE_CLIENT_SECRET=<INSERT_HERE>

# Go to https://auth.globus.org/v2/web/developers
# and create credentials that you will use
export GLOBUS_CLIENT_ID=<INSERT_HERE>
export GLOBUS_CLIENT_SECRET=<INSERT_HERE>

export FLASK_APP=app.py
flask run
