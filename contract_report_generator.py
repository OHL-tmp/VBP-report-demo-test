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
                    html.Div([Header_mgmt(app, False, False, True, False)], style={"height":"6rem"}, className = "sticky-top navbar-expand-lg"),
                    
                    html.Div(
                    	[
                    		html.Div(
                    			[
                    				html.H1("Report Generator", style={"padding-left":"0px","padding-bottom":"30px"}),
		       #              		dbc.Row([
									# 	dbc.Col(html.H2('Generating report for ', style={"font-size":"1rem"}),width="auto"),
									# 	dbc.Col([
									# 		dcc.Dropdown(options = [{'label':'ACO report', 'value':'ACO report'},
									# 			{'label':'Bundle report)', 'value':'Bundle report'}],
									# 			value = "ACO report",clearable = False,style={"font-size":"0.8rem","font-family":"NotoSans-Light"}),

									# 		],
									# 		style={"margin-top":"-0.5rem"},
									# 		width=5)
									# 	],
									# 	style={"padding-bottom":"1rem"}
									# ),
									html.Hr(style={"padding-bottom":"2rem"}),
									dbc.Row(
										[
											dbc.Col(width=1),
											dbc.Col(
												# html.H1("Change View", style={"font-size":"0.8rem","text-align":"center","color":"#1357DD"}),
												# style={"padding-top":"10px","padding-bottom":"50px","background-color":"#a8c8ff","border-radius":"0.5rem"},
												width=7),
											dbc.Col(width=2),
											dbc.Col(
												html.H1("Download/Print", style={"font-size":"0.8rem","text-align":"center","color":"#1357DD"}),
												style={"padding-top":"10px","padding-bottom":"50px","background-color":"#a8c8ff","border-radius":"0.5rem"},
												width=2)
										],
										style={"padding-bottom":"10px"}
									),
                    			],
		                    	style={"padding":"20px","padding-bottom":"0rem", "width":"850px", "margin":"auto","position":"relative","z-index":"-1"},
                    		),
                    		
	                    	html.Div(
		                        [
		                        	
			                        div_report_content(app),
			                    ],
		                        className="mb-3",
		                    	style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)","background-color":"#fff","padding":"0px","padding-bottom":"0rem", "width":"850px", "margin":"auto","margin-top":"-3.5rem"},

		                    )
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