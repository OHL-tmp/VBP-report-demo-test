#!/usr/bin/env python3

import dash
import dash_auth

from config.login import *

app = dash.Dash(__name__, url_base_pathname='/vbc-demo/launch/')

server = app.server

app.config.suppress_callback_exceptions = True


auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
