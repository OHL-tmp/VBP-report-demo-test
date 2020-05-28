import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import os
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
		dbc.Button("Input & Edit Assumption", id = 'button-edit-assumption', style={"border-radius":"5rem"}),
								dbc.Modal([
									dbc.ModalHeader(html.H1("Input & Edit Assumption", style={"font-family":"NotoSans-Black","font-size":"1.5rem"})),
									dbc.ModalBody([
										input_session(),
										]),
									dbc.ModalFooter(
										dbc.Button("SAVE", id = 'close-edit-assumption')
										)
									], id = 'modal-edit-assumption', size="xl", is_open = False, backdrop = 'static'),
		])

def input_session():
	return dbc.ListGroup([
		dbc.ListGroupItem([html.H4("Client Input Assumptions")]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Plan Information", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText(
				[
					dbc.Row(
						[
							dbc.Col("Plan Type", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
							dbc.Col(dbc.Input(value = "MAPD", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
						], style={"padding-top":"1rem"}
					),
					dbc.Row(
						[
							dbc.Col("Total Members", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
							dbc.Col(dbc.Input(value = "150,000", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
						], style={"padding-top":"1rem"}
					),
					dbc.Row(
						[
							dbc.Col("Age Distribution", style={"font-family":"NotoSans-Regular","font-size":"1rem"}, width=3),
							dbc.Col([
								dbc.Button("\u25BC", id = 'button-collapse-age', size="sm", color='primary', style={"border-radius":"10rem"}),
								],
								width=1),
							dbc.Col(
								html.Div(['Fill below or ',
										html.Br(),
										html.A('Download Template', 
											id = 'download-age',
											href='http://139.224.186.182:8098/downloads/Age Distribution template.xlsx',
											target = "_blank")
										], style={"font-size":"0.8rem"}),
								width=2
								),
							dbc.Col(
								dcc.Upload(
									id = 'upload-age',
									children = html.Div([
										'Select Related Files to Upload'
										],style={"font-family":"NotoSans-Regular","font-size":"0.8rem","text-decoration":"underline","color":"#1357DD"}),
									style={
										'height': '40px',
										'lineHeight': '40px',
										'borderWidth': '1px',
										'borderStyle': 'dashed',
										'borderRadius': '5px',
										'textAlign': 'center'
										}
									), width=3
								),
							dbc.Col(
								html.Div(id = 'output-age-upload', style={"text-align":"center","padding":"0.5rem","font-family":"NotoSans-Regular","font-size":"0.6rem"}),
								width=3,
								)
						], style={"padding-top":"1rem"}
					),
					html.Div(
						dbc.Collapse(
							[
								card_collapse_age()
							],
							id = 'collapse-age', is_open = False,
							style={"padding":"1rem","border-radius":"0.5rem","background-color":"#f5f5f5"}
						), style={"padding":"0.5rem"}
					),
					dbc.Row([
						dbc.Col("Gender Distribution", style={"font-family":"NotoSans-Regular","font-size":"1rem"}, width=3),
						dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-gender'))
						], style={"padding-top":"1rem"}),
					html.Div(
						dbc.Collapse(
							[
								card_collapse_gender()
								
							],id = 'collapse-gender', is_open = False,
							style={"padding":"1rem","border-radius":"0.5rem","background-color":"#f5f5f5"}
						), style={"padding":"0.5rem"}
					),
					dbc.Row([
						dbc.Col("Geography Distribution", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col(
								html.Div([
										html.A('Download Template', 
											id = 'download-geo',
											href='http://139.224.186.182:8098/downloads/Geographic Distribution template.xlsx',
											target = "_blank")
										]),
								),
						dbc.Col(
							dcc.Upload(
								id = 'upload-geo',
								children = html.Div([
									'Select Related Files to Upload'
									],style={"font-family":"NotoSans-Regular","font-size":"0.8rem","text-decoration":"underline","color":"#1357DD"}),
								style={
									'height': '40px',
									'lineHeight': '40px',
									'borderWidth': '1px',
									'borderStyle': 'dashed',
									'borderRadius': '5px',
									'textAlign': 'center'
									}
								), width = 3
							),
						dbc.Col(
							html.Div(id = 'output-geo-upload', style={"text-align":"center","padding":"0.5rem","font-family":"NotoSans-Regular","font-size":"0.6rem"}),
							)
						], style={"padding-top":"1rem"}),
					dbc.Row([
						dbc.Col("Pharmacy Benefit Design", style={"font-family":"NotoSans-Regular","font-size":"1rem"}, width=3),
						dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-benefit'))
						], style={"padding-top":"1rem"}),
					html.Div(
						dbc.Collapse(
							[
								card_collapse_tier()
							],
							id = 'collapse-benefit', 
							is_open = False,
							style={"padding":"1rem","border-radius":"0.5rem","background-color":"#f5f5f5"}
						), style={"padding":"0.5rem"}
					),
				]
			),
			]
		),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Drug Information", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Formulary Tier for Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "Tier 3", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Entresto Pricing Information", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "$9.6 / unit (tablet)", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					dbc.Col(
							dcc.Upload(
								id = 'upload-price',
								children = html.Div([
									'Select Related Files to Upload'
									],style={"font-family":"NotoSans-Regular","font-size":"0.8rem","text-decoration":"underline","color":"#1357DD"}),
								style={
									'height': '40px',
									'lineHeight': '40px',
									'borderWidth': '1px',
									'borderStyle': 'dashed',
									'borderRadius': '5px',
									'textAlign': 'center'
									}
								), width = 3
							),
					dbc.Col(
						html.Div(id = 'output-price-upload', style={"text-align":"center","padding":"0.5rem","font-family":"NotoSans-Regular","font-size":"0.6rem"}),
						)
					], style={"padding-top":"1rem"}),
				
				]),
			]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Value Based Measures", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Assumptions for Value Based Measure", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(
						dbc.Button("Measure Library Preview", color = 'link', href = "/vbc-demo/contract-optimizer/measures-library/")
						),
					dbc.Col(download_template()),
						], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col(
						dcc.Upload(
						id = 'upload-data',
						children = html.Div([
							'Select Related Files to Upload'
							],style={"font-family":"NotoSans-Regular","font-size":"1rem","text-decoration":"underline","color":"#1357DD"}),
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
					], style={"padding-top":"1rem", "text-align":"center"}),
				]),
			]),
		dbc.ListGroupItem([html.H4("Modeling Assumptions")]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("CHF Prevalence Rate", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Projected CHF Patients as a % of Total Plan Members", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "13.6%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				
			]),
		]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("CHF Patient Cost and Utilization Assumptions", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("CHF Related Cost PPPY (Per Patient Per Year) Before Taking Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "$ 25,000", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual CHF Related Cost PPPY Trend Before Taking Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "7%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Assumptions by Patient Cohort and Service Category Workbook", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(
							html.Div([
									html.A('Download Workbook', 
										id = 'download-cohort',
										href='http://139.224.186.182:8098/downloads/CHF Cost and Utilization Assumptions.xlsx',
										target = "_blank")
									]),
							),
					], style={"padding-top":"1rem"}),

				]),
			]),


		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Entresto Market Share", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Projected Entresto Utilizer as a % of Total CHF Population", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "7%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Entresto Utilizer Monthly Ramp Up Rate", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-month'))
					], style={"padding-top":"1rem"}),
				html.Div(
					dbc.Collapse(
						[
							card_collapse_month()
						],
						id = 'collapse-month', 
						is_open = False,
						style={"padding":"1rem","border-radius":"0.5rem","background-color":"#f5f5f5"}
					), style={"padding":"0.5rem"}
				),
				]),
			]),
		],
		style={"border-radius":"0.5rem"})

def card_collapse_age():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Age Band", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Member %", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Newborn (0-1m)", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("1m-2y", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("2-12", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("12-17", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("18-24", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("25-34", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("35-44", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("45-54", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("55-64", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("65-74", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("75-84", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col(">=85", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding":"1rem"}
		)

def card_collapse_gender():
	return dbc.Card([
				dbc.Row([
					dbc.Col("Gender", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Member %", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Female", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "53%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Male", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "47%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding":"1rem"})


def card_collapse_tier():
	return dbc.Card(
			[
				dbc.Row(
					[
						dbc.Col("Tier", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col("Days of Supply", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col("Copay", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col("Coinsurance (% of Allowed)", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col("Max Copay", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 1", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("30",style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(value = "$5", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 1", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("90", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(value = "$10", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 2", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("30", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(value = "$10", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 2", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("90", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(value = "$20", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 3", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("30", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(value = "$40",bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 3", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("90", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(value = "$100",bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 4", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("30", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(value = "$70",bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 4", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("90", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(value = "$150",bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 5", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("30", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "20%",bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "$200",bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 5", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col("90", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.Col(dbc.Input(bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "20%",bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "$400",bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Maximum OOP per Individual", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col(dbc.Input(value = '$2800', bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
			],
			style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding":"1rem"}
		)



def card_collapse_month():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Month", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Ramp Up", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 1", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "5%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 2", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "12%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 3", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "23%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 4", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "41%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 5", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "68%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 6", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 7", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 8", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 9", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 10", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 11", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 12", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding":"1rem"}
		)

def download_template():
	return html.A(
							# children=dbc.Button(
							#     "Download the template file",
							#     id='download-template',
							#     color= 'link',
							# ),
							"Download the template file",
							id = 'download-link',
							href='http://139.224.186.182:8098/downloads/Pharma Value-Based Measures Template.xlsx',
							# download="test.xlsx",
							target = "_blank"
						)
