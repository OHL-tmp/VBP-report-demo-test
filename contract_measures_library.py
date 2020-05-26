import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import time

import datetime
import json
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output, State

from utils import *

from app import app

def create_layout(app):
	return html.Div(
                [ 
                    html.Div([Header_contract(app, False, True, False, False)], style={"height":"6rem"}, className = "sticky-top navbar-expand-lg"),
                    
                    html.Div(
                    	[
                    		html.Div(html.H1("Measures Library")),
                    		html.Div(),
                    	]
                    )
                    
                ])

def div_report_content(app):
	return html.Div(
			[
				html.Div(
					html.Embed(src=app.get_asset_url("pharma-report.pdf"), width="100%", height="1150px")
				),
				
			]
		)



layout = create_layout(app)

if __name__ == "__main__":
    app.run_server(host="127.0.0.1",debug=True,port=8052)