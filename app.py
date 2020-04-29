#!/usr/bin/env python3

import dash


app = dash.Dash(__name__, url_base_pathname='/vbc-demo/launch/')

server = app.server

app.config.suppress_callback_exceptions = True