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
from figure import *

app = dash.Dash(__name__, url_base_pathname='/vbc-demo/measure-library/')

server = app.server

df_measure_library = pd.read_csv("data/measure_library.csv")

def create_layout(app):
	return html.Div(
                [ 
                    # html.Div([Header_contract(app, False, True, False, False)], style={"height":"6rem"}, className = "sticky-top navbar-expand-lg"),
                    # html.Div(dbc.Button('Back to Contract Optimizer', href = "/vbc-demo/contract-optimizer/",style={"text-align":"center", "font-size":"0.8rem", "border":"1px dashed #919191"}, color="light"), style={"text-align":"start", "padding":"1rem"}),
	                
                    html.Div(
                    	[
                    		html.Div(html.H1("Measures Library")),
                    		html.Div(children=measure_lib(df_measure_library)),
                    	],
                    	style={"padding":"1rem","height":"100rem"}
                    )
                    
                ])




#layout = create_layout(app)
app.layout = create_layout(app)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0",debug=True,port=8097)