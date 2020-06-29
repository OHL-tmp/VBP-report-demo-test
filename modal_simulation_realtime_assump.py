import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import os
import pandas as pd
import numpy as np
import datetime

from dash.dependencies import Input, Output, State

from app import app

def modal_simulation_assump():
	return html.Div([
		dbc.Button("Model Assumptions", id = 'button-edit-realtime-assumption', style={"border-radius":"5rem"}),
								dbc.Modal([
									dbc.ModalHeader(html.H1("Model Assumptions", style={"font-family":"NotoSans-Black","font-size":"1.5rem"})),
									dbc.ModalBody([
										realtime_assump_session(),
										]),
									dbc.ModalFooter(
										dbc.Button("SAVE", id = 'close-edit-realtime-assumption')
										)
									], id = 'modal-edit-realtime-assumption', size="xl", is_open = False, backdrop = 'static'),
		])

def realtime_assump_session():
	return html.Div([
		dbc.Row([
			dbc.Col('Entresto Tier'),
			dbc.Col(dcc.Dropdown(
						options = [{'label':'Tier 1', 'value':1},{'label':'Tier 2', 'value':2},{'label':'Tier 3', 'value':3},{'label':'Tier 4', 'value':4},{'label':'Tier 5', 'value':5}],
						persistence = True,
						persistence_type = 'session',
						id = 'realtime-assump-dropdown-tier',
						value = 3,

					)
				),
			], style={"padding-top":"0.5rem"}),
		html.Hr(),
		html.Div([
			html.H2('Rebate', style={"font-size":"1.2rem"}),
			], style={"padding":"1rem"}),
		dbc.Row([
			dbc.Col('Base Rebate without VBC', width=3),
			dbc.Col([
				dbc.InputGroup([
					dbc.Input(id = 'realtime-assump-input-rebatenovbc',type = 'number',
							persistence = True, value = 40,
							persistence_type = 'session'),
					dbc.InputGroupAddon('%', addon_type = 'append'),
					], size="sm")
				], width=2),
			dbc.Col(
				dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'realtime-assump-button-collapse-rebatenovbc'), width=1
				),
			dbc.Col('Base Rebate with VBC', width=3),
			dbc.Col([
				dbc.InputGroup([
					dbc.Input(id = 'realtime-assump-input-rebatevbc',type = 'number',
							persistence = True, value = 40,
							persistence_type = 'session'),
					dbc.InputGroupAddon('%', addon_type = 'append'),
					], size="sm")
				], width=2),
			dbc.Col(
				dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'realtime-assump-button-collapse-rebatevbc'), width=1
				),
			], style={"padding-top":"0.5rem"}),
		dbc.Row([
			dbc.Col(dbc.Collapse(
				collapse_rebatenovbc(),
				id = 'realtime-assump-collapse-rebatenovbc'
				)),
			dbc.Col(dbc.Collapse(
				collapse_rebatevbc(),
				id = 'realtime-assump-collapse-rebatevbc'
				)),
			], style={"padding-top":"0.5rem"}),
		html.Hr(),
		html.Div([
			html.H2('Entresto Utilization Pattern', style={"font-size":"1.2rem"}),
			], style={"padding":"1rem"}),
		dbc.Row([
			dbc.Col('Expected Entresto Utilizer as a % of Total CHF Patients',width=6),
			dbc.Col([
				dbc.InputGroup([
					dbc.Input(id = 'realtime-assump-input-utilizer',type = 'number', value = 7,
							persistence = True,
							persistence_type = 'session'),
					dbc.InputGroupAddon('%', addon_type = 'append')
					], size="sm")
				], width=2)
			], style={"padding-top":"0.5rem"}),
		dbc.Row([
			dbc.Col('Entresto Market Share Monthly Ramp Up Rate (M1-M12)',width=6),
			dbc.Col(
				dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'realtime-assump-button-collapse-rampup')
				)
			], style={"padding-top":"0.5rem"}),
		html.Div(
					dbc.Collapse(
						[
							card_collapse_rampup()
						],
						id = 'realtime-assump-collapse-rampup', 
						is_open = False,
						style={"padding":"1rem","border-radius":"0.5rem","background-color":"#f5f5f5"}
					), style={"padding":"0.5rem"}
				),
		dbc.Row([
			dbc.Col('Expected Average Script PPPM for Entresto Utilizer',width=6),
			dbc.Col([
				dbc.InputGroup([
					dbc.Input(id = 'realtime-assump-input-script',type = 'number', value = 0.8,
							persistence = True,
							persistence_type = 'session')
					], size="sm")
				], width=2),
			], style={"padding-top":"0.5rem"}),
		html.Hr(),
		html.Div([
			html.H2('CHF Patient Cost and Utilization Trend', style={"font-size":"1.2rem"}),
			], style={"padding":"1rem"}),
		dbc.Row([
			dbc.Col('Projected Annual CHF Related Medical Cost Trend', width=6),
			dbc.Col([
				dbc.InputGroup([
					dbc.Input(id = 'realtime-assump-input-trend',type = 'number',  value = 0,
							persistence = True,
							persistence_type = 'session'),
					dbc.InputGroupAddon('%', addon_type = 'append')
					],size="sm")
				],width=2),
			], style={"padding-top":"0.5rem"}),
		dbc.Row([
			dbc.Col('Projected Annual Change in CHF Related Inpatient Rates (per 1,000 CHF patients)',width=6),
			dbc.Col([
				dbc.InputGroup([
					dbc.Input(id = 'realtime-assump-input-iprate',type = 'number',  value = 0,
							persistence = True,
							persistence_type = 'session'),
					dbc.InputGroupAddon('%', addon_type = 'append')
					],size="sm")
				],width=2),
			], style={"padding-top":"0.5rem"}),
		html.Hr(),
		html.Div([
			html.H2('Entresto Efficacy', style={"font-size":"1.2rem"}),
			], style={"padding":"1rem"}),
		dbc.Row([
			dbc.Col('Projected Reduction in CHF Related Hospitalization',width=6),
			dbc.Col([
				dbc.InputGroup([
					dbc.Input(id = 'realtime-assump-input-hospitalization',type = 'number',  value = 10,
							persistence = True,
							persistence_type = 'session'),
					dbc.InputGroupAddon('%', addon_type = 'append')
					],size="sm")
				],width=2)
			], style={"padding-top":"0.5rem"}),
		dbc.Row([
			dbc.Col('Projected LVEF LS Mean Change %',width=6),
			dbc.Col([
				dbc.InputGroup([
					dbc.Input(id = 'realtime-assump-input-lvef',type = 'number',  value = 3,
							persistence = True,
							persistence_type = 'session'),
					dbc.InputGroupAddon('%', addon_type = 'append')
					],size="sm")
				], width=2)
			], style={"padding-top":"0.5rem"}),
		dbc.Row([
			dbc.Col('Projected NT-proBNP Change %',width=6),
			dbc.Col([
				dbc.InputGroup([
					dbc.InputGroupAddon('-', addon_type = 'preprend'),
					dbc.Input(id = 'realtime-assump-input-probnp',type = 'number', value = 25,
							persistence = True,
							persistence_type = 'session'),
					dbc.InputGroupAddon('%', addon_type = 'append')
					],size="sm")
				],width=2)
			], style={"padding-top":"0.5rem"}),
		])

def collapse_rebatenovbc():
	return dbc.Card(
		[
			dbc.Row([
				dbc.Col("% of market share range", style={"font-size":"0.8rem"}),
				dbc.Col("Rebate %", style={"font-size":"0.8rem"}),
				],
				style={"padding":"0.5rem"}),
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-l-1-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'novbc-r-1-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-p-1-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatenovbc-1', hidden = False),
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-l-2-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'novbc-r-2-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-p-2-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatenovbc-2', hidden = True),
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-l-3-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'novbc-r-3-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-p-3-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatenovbc-3', hidden = True),
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-l-4-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'novbc-r-4-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-p-4-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatenovbc-4', hidden = True),
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-l-5-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'novbc-r-5-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'novbc-p-5-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatenovbc-5', hidden = True),
			dbc.Row(
				[
				dbc.Col(),
				dbc.Col(dbc.Button('Add another row (up to 5)', style={"font-size":"0.8rem"}, id = 'realtime-assump-button-addrebatenovbc'), width=5),
				], style={"padding":"0.5rem"}
				),
		],style={"background-color":"#f5f5f5","border-radius":"0.5rem"}
		)


def collapse_rebatevbc():
	return dbc.Card(
		[
			dbc.Row([
				dbc.Col("% of market share range", style={"font-size":"0.8rem"}),
				dbc.Col("Rebate %", style={"font-size":"0.8rem"}),
				],
				style={"padding":"0.5rem"}),
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-l-1-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'vbc-r-1-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-p-1-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatevbc-1', hidden = False),
			
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-l-2-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'vbc-r-2-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-p-2-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatevbc-2', hidden = True),
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-l-3-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'vbc-r-3-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-p-3-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatevbc-3', hidden = True),
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-l-4-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'vbc-r-4-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-p-4-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatevbc-4', hidden = True),
			html.Div([
				dbc.Row([
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-l-5-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						dbc.InputGroupAddon('~', addon_type = 'append'),
						dbc.Input(id = 'vbc-r-5-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					dbc.Col(dbc.InputGroup([
						dbc.Input(id = 'vbc-p-5-input',type = 'number',
							persistence = True,
							persistence_type = 'session'),
						dbc.InputGroupAddon('%', addon_type = 'append'),
						], size="sm")),
					],
					style={"padding":"0.5rem"})
				], id = 'realtime-assump-div-rebatevbc-5', hidden = True),
			dbc.Row(
				[
				dbc.Col(),
				dbc.Col(dbc.Button('Add another row (up to 5)', style={"font-size":"0.8rem"}, id = 'realtime-assump-button-addrebatevbc'), width=5),
				], style={"padding":"0.5rem"}
				),
		],style={"background-color":"#f5f5f5","border-radius":"0.5rem"}
		)

def card_collapse_rampup():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Month", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Ramp Up", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 1", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
						dbc.Input(id = 'realtime-assump-month-1',value = 2, type = 'number',bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
						dbc.InputGroupAddon('%', addon_type = 'append')])
						)
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 2", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-2',value = 3, type = 'number',bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 3", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-3',value = 4, type = 'number',bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 4", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-4',value = 5,type = 'number', bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 5", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-5',value = 6,type = 'number', bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 6", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-6',value = 7,type = 'number', bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 7", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-7',value = 7,type = 'number', bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 8", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-8',value = 7, type = 'number',bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 9", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-9',value = 7, type = 'number',bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 10", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-10',value = 7, type = 'number',bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 11", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-11',value = 7, type = 'number',bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 12", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(
						dbc.InputGroup([
							dbc.Input(id = 'realtime-assump-month-12',value = 7, type = 'number',bs_size="sm", persistence = True, persistence_type = 'session', style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}),
							dbc.InputGroupAddon('%', addon_type = 'append')]))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding":"1rem"}
		)