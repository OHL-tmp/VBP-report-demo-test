
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import pandas as pd
import numpy as np

import pathlib
#import visdcc
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State
from utils import *
from figure import *
from modal_dashboard_domain_selection import *

from app import app




def create_layout(app):
	return html.Div(
			html.Div(
				[ 
					html.Div(
                        [
                            dbc.Button(
                            	"Patient Portal", 
                            	color="light", 
                            	className="mr-1", 
                            	href = "http://139.224.186.182:8095/login/",
                                target= "_blank",
                                style={"width":"300px","height":"160px","border-radius":"0.8rem", "font-family":"NotoSans-Black", "font-size":"2.2rem", "color":"#fff", "border":"1px solid #1357dd","background":"#1357dd","padding":"30px","box-shadow":"0 4px 8px 0 rgba(19, 86, 221, 0.4), 0 6px 20px 0 rgba(19, 86, 221, 0.1)"}
                            ), 
                            dbc.Button(
                            	"Physician Portal", 
                            	color="light", 
                            	className="mr-1", 
                            	href = "http://139.224.186.182:8094/physician/", 
                                target= "_blank",
                            	style={"width":"300px","height":"160px","border-radius":"0.8rem", "font-family":"NotoSans-Black", "font-size":"2.2rem", "color":"#fff", "border":"1px solid #dc3545","background":"#dc3545","padding":"30px","box-shadow":"0 4px 8px 0 rgba(220, 53, 70, 0.4), 0 6px 20px 0 rgba(220, 53, 70, 0.1)"}
                            ), 
                            dbc.Button(
                                "Back to Home", 
                                color="light", 
                                className="mr-1", 
                                href = "/", 
                                style={"width":"300px","height":"160px","border-radius":"0.8rem", "font-family":"NotoSans-Black", "font-size":"2.2rem", "color":"#000", "border":"1px solid #f7f7f7","background":"#f7f7f7","padding":"30px","box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.4), 0 6px 20px 0 rgba(0, 0, 0, 0.1)"}
                            ),
                        ],
                        style={"background-color":"none", "border":"none","padding-top":"35vh","display":"flex","justify-content":"space-around"}
                    )
				],
				style={"width":"100vh", "margin":"auto","text-align":"center"}
			),
			style={"height":"100vh"}
		)
	


layout = create_layout(app)






