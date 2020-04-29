import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import pandas as pd
import numpy as np
import datetime

import pathlib
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State

from app import app

def modal_simulation_input():
	return html.Div([
		dbc.Button("Edit Assumption", id = 'button-edit-assumption', style={"border-radius":"5rem"}),
                                dbc.Modal([
                                    dbc.ModalHeader(html.H1("Edit Assumption", style={"font-family":"NotoSans-Black","font-size":"1.5rem"})),
                                    dbc.ModalBody([
                                    	input_session(),
                                    	]),
                                    dbc.ModalFooter(
                                        dbc.Button("SAVE", id = 'close-edit-assumption')
                                        )
                                    ], id = 'modal-edit-assumption', size="xl", is_open = True),
		])

def input_session():
	return dbc.ListGroup([
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Plan Info", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Plan Type", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "MAPD", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Age Distribution", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col([
						dbc.Button("···", id = 'button-popover-age', size="sm", color='primary', style={"border-radius":"10rem"}),
						dbc.Popover([
							dbc.PopoverHeader("Age Distribution", style={"font-family":"NotoSans-SemiBold","font-size":"1rem"}),
							dbc.PopoverBody([dbc.Row([
									dbc.Col("Age Band", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
									dbc.Col("Member %", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
									], style={"padding-top":"1rem"}),
								dbc.Row([
									dbc.Col("<65", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
									dbc.Col(dbc.Input(value = "12%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
									], style={"padding-top":"1rem"}),
								dbc.Row([
									dbc.Col("65-74", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
									dbc.Col(dbc.Input(value = "48%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
									], style={"padding-top":"1rem"}),
								dbc.Row([
									dbc.Col("75-84", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
									dbc.Col(dbc.Input(value = "27%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
									], style={"padding-top":"1rem"}),
								dbc.Row([
									dbc.Col(">=85", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
									dbc.Col(dbc.Input(value = "13%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
									], style={"padding-top":"1rem"}),
								dbc.Row([
									dbc.Col(dbc.Button("Save", id = 'popover-age-submit', size="sm", color='primary')),
									], style={"padding":"2rem","text-align":"center"}),
								], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}),
							
							],id = 'popover-age', is_open = False, target = 'button-popover-age')
						])
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Gender Distribution", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Region", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "TBD", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Entresto Formulary Tier", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "Preferred Brand", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Patient Cost Share for Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
				]),
			]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Entresto Utilizer Info", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Expected Entresto Utilizer as a % of total CHF Population", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
				]),
			]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Assumptions for  Entresto Outcome Related Measures", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Assumptions for Each Measure", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(html.A('Download the template file'), style={"font-family":"NotoSans-Regular","font-size":"1rem","text-decoration":"underline","color":"#1357DD"}),
						], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col(
						dcc.Upload(
						id = 'upload-data',
						children = html.Div([
							'Drag and Drop or ',
							html.A('Select Files')
							]),
						style={
							'height': '60px',
							'lineHeight': '60px',
							'borderWidth': '1px',
							'borderStyle': 'dashed',
							'borderRadius': '5px',
							'textAlign': 'center',
							'margin': '10px'
							}
						),style={"padding-top":"1rem"}, width=12),
					]),
				dbc.Row([
					html.Div(id = 'output-data-upload', style={"text-align":"center","padding":"0.5rem","font-family":"NotoSans-Regular","font-size":"0.6rem"}),
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Probability range for low/mid/high likelihood (to achieve target)", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Pharma's risk tolerance level (i.e., probability rebate adjustment will hit the negative cap)", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "5%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				]),
			]),
		],
		style={"border-radius":"0.5rem"})





