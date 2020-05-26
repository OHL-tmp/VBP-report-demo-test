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
                                    ], id = 'modal-edit-assumption', size="xl", is_open = True, backdrop = 'static'),
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
							dbc.Col(dbc.Input(value = "MAPD", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
						], style={"padding-top":"1rem"}
					),
					dbc.Row(
						[
							dbc.Col("Total Members", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
							dbc.Col(dbc.Input(value = "150,000", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
						], style={"padding-top":"1rem"}
					),
					dbc.Row(
						[
							dbc.Col("Age Distribution", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
							dbc.Col([
								dbc.Button("\u25BC", id = 'button-collapse-age', size="sm", color='primary', style={"border-radius":"10rem"}),
								])
						], style={"padding-top":"1rem"}
					),
					html.Div(
						dbc.Collapse(
							[
								card_collapse_age()
							],
							id = 'collapse-age', is_open = False
						)
					),
					dbc.Row([
						dbc.Col("Gender Distribution", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-gender'))
						], style={"padding-top":"1rem"}),
					html.Div(
						dbc.Collapse(
							[
								card_collapse_gender()
								
							],id = 'collapse-gender', is_open = False
						)
					),
					dbc.Row([
						dbc.Col("Region", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col(dbc.Input(value = "Northeast", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
						], style={"padding-top":"1rem"}),
					dbc.Row([
						dbc.Col("MSA (if applicable)", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col(dbc.Input(value = "New York-Newark-Jersey City, NY-NJ-PA MSA", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
						], style={"padding-top":"1rem"}),
					dbc.Row([
						dbc.Col("Formulary Tier for Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col(dbc.Input(value = "Preferred Brand", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
						], style={"padding-top":"1rem"}),
					dbc.Row([
						dbc.Col("Pharmacy Benefit Design", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
						dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-benefit'))
						], style={"padding-top":"1rem"}),
					html.Div(
						dbc.Collapse(
							[
								card_collapse_tier()
							],
							id = 'collapse-benefit', 
							is_open = False,
						)
					),
				]
			),
			]
		),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Drug Information", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Entresto Pricing Information", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "$9.6 / unit (tablet)", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Assumptions for Each Measure", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
#					dbc.Col(html.A('Download the template file'), style={"font-family":"NotoSans-Regular","font-size":"1rem","text-decoration":"underline","color":"#1357DD"}),
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
					], style={"padding-top":"1rem"}),
				]),
			]),
		dbc.ListGroupItem([html.H4("Modeling Assumptions")]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("CHF Prevalence Rate & Severity Assumptions", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Projected CHF Patients as a % of Total Plan Members", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "13.6%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("CHF Comorbidity Condition", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-comorbidity'))
					], style={"padding-top":"1rem"}),
				html.Div(
					dbc.Collapse(
						[
							card_collapse_comorbidity()
						],
						id = 'collapse-comorbidity', 
						is_open = False,
					)
				),
			]),
		]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("CHF Patient Cost and Utilization Assumptions", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("CHF Patient Cost Assumptions", style={"font-family":"NotoSans-Regular","font-size":"1.2rem"}),
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Total Cost PPPY (Per Patient Per Year) Before Taking Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "$ 42,000", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("CHF Related Cost as a % of Total Cost", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "60%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Total Cost PPPY by Service Category", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-totalcost-srvc'))
					], style={"padding-top":"1rem"}),
				html.Div(
					dbc.Collapse(
						[
							card_collapse_totalcost_srvc()
						],
						id = 'collapse-totalcost-srvc', 
						is_open = False,
					)
				),
				dbc.Row([
					dbc.Col("Total Cost PPPY by Patient Cohort", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-totalcost-patient'))
					], style={"padding-top":"1rem"}),
				html.Div(
					dbc.Collapse(
						[
							card_collapse_totalcost_patient()
						],
						id = 'collapse-totalcost-patient', 
						is_open = False,
					)
				),


				dbc.Row([
					dbc.Col("CHF Patient Cost Trend Assumptions", style={"font-family":"NotoSans-Regular","font-size":"1.2rem"}),
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual PPPY Cost Trend Before Taking Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "7%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual PPPY Cost Trend by Service Category", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-annucost-srvc'))
					], style={"padding-top":"1rem"}),
				html.Div(
					dbc.Collapse(
						[
							card_collapse_annucost_srvc()
						],
						id = 'collapse-annucost-srvc', 
						is_open = False,
					)
				),
				dbc.Row([
					dbc.Col("Annual PPPY Cost Trend by Patient Cohort", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-annucost-patient'))
					], style={"padding-top":"1rem"}),
				html.Div(
					dbc.Collapse(
						[
							card_collapse_annucost_patient()
						],
						id = 'collapse-annucost-patient', 
						is_open = False,
					)
				),


				dbc.Row([
					dbc.Col("CHF Patient Utilization Assumptions", style={"font-family":"NotoSans-Regular","font-size":"1.2rem"}),
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Projected Inpatient Admissions PPPY Before Taking Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "1.4", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("CHF Related Inpatient Admissions as a % of Total Admissions", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "80%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Total Inpatient Admissions PPPY by Medical Condition", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-ad-condition'))
					], style={"padding-top":"1rem"}),
				html.Div(
					dbc.Collapse(
						[
							card_collapse_ad_condition()
						],
						id = 'collapse-ad-condition', 
						is_open = False,
					)
				),

				dbc.Row([
					dbc.Col("Total Inpatient Admissions PPPY by Patient Cohort", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-ad-patient'))
					], style={"padding-top":"1rem"}),
				html.Div(
					dbc.Collapse(
						[
							card_collapse_ad_patient()
						],
						id = 'collapse-ad-patient', 
						is_open = False,
					)
				),



				dbc.Row([
					dbc.Col("CHF Patient Utilization Trend Assumptions", style={"font-family":"NotoSans-Regular","font-size":"1.2rem"}),
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual PPPY Inpatient Utilization Trend Before Taking Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "5.4%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual PPPY Inpatient Utilization Trend by Patient Cohort", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("\u25BC", size="sm", color='primary', style={"border-radius":"10rem"}, id = 'button-collapse-utili-patient'))
					], style={"padding-top":"1rem"}),
				html.Div(
					dbc.Collapse(
						[
							card_collapse_utili_patient()
						],
						id = 'collapse-utili-patient', 
						is_open = False,
					)
				),

				]),
			]),


		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Entresto Utilization Assumptions", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Projected Entresto Utilizer as a % of Total CHF Population", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "7%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
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
					)
				),
				dbc.Row([
					dbc.Col("Average Entresto Script PPPY (Per Patient Per Year)", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "6.9", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Average Units/ Script", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "70", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
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
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def card_collapse_gender():
	return dbc.Card([
				dbc.Row([
					dbc.Col("Gender", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Member %", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Female", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "53%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Male", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "47%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"})


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
						dbc.Col("Tier 1 (Generic)", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col(dbc.Input(value = "30", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "$10", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 1 (Generic)", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col(dbc.Input(value = "90", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "$20", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 2 (Preferred Brand)", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col(dbc.Input(value = "30", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "$40", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 2 (Preferred Brand)", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col(dbc.Input(value = "90", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "$100", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 3 (Non-Preferred Brand)", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col(dbc.Input(value = "30", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "20%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "$200", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Tier 3 (Non-Preferred Brand)", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col(dbc.Input(value = "90", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "20%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = "$400", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
				dbc.Row(
					[
						dbc.Col("Maximum OOP per Individual", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(value = '$2800', bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
						dbc.Col(dbc.Input(disabled = True, bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"})),
					], style={"padding-top":"1rem"}
				),
			],
			style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def card_collapse_comorbidity():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Comorbidity Type", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("% of CHF Patients", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Hypertension", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "89%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Coronary heart disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "68%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Chronic pulmonary disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "64%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Renal disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "54%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Atrial fibrillation", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "53%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Diabetes", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "48%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Cerebrovascular disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "37%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def card_collapse_totalcost_srvc():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Service Category", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("% of Total Cost PPPY", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Inpatient", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "55.4%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Outpatient Others (Non ER)", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "15.2%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Outpatient ER", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "5.2%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Professional Services", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "11.5%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Drug", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "10.2%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Skilled Nursing Facilit", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "1.4%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Home Health", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.6%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Hospice", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.4%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def card_collapse_totalcost_patient():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Comorbidity Type", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Total Cost PPPY", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("No-Comorbidity", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "$22680", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Hypertension", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "$25200", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Coronary heart disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "$27720", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Chronic pulmonary disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "$33264", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Renal disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "$39312", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Atrial fibrillation", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "$30492", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Diabetes", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "$30240", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Cerebrovascular disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "$33516", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def card_collapse_annucost_srvc():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Service Category", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Trend", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Inpatient", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "6.0%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Outpatient Others (Non ER)", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "8.0%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Outpatient ER", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "8.0%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Professional Services", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "9.0%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Drug", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "8.0%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Skilled Nursing Facilit", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "4.0%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Home Health", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "4.0%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Hospice", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "4.0%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def card_collapse_annucost_patient():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Comorbidity Type", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Trend", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("No-Comorbidity", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "6%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Hypertension", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "8%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Coronary heart disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "8%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Chronic pulmonary disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "4%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Renal disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "9%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Atrial fibrillation", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "6%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Diabetes", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "4%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Cerebrovascular disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "7%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def card_collapse_ad_condition():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Condition", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Inpatient Adm PPPY", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Heart Failure", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.49", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Renal Failure", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.08", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Pleural effusion", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.04", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Acute myocardial infarction", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.02", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Cardiac Arrhythmia", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.18", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Cardiac arrest and ventricular fibrillation", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.02", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Hypertension", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.07", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("CABG", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.10", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Pacemaker Implant", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.01", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("PCI", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.06", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("ICD", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.05", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def card_collapse_ad_patient():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Comorbidity Type", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Inpatient Adm PPPY", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("No-Comorbidity", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "0.90", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Hypertension", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "1.00", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Coronary heart disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "1.10", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Chronic pulmonary disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "1.32", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Renal disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "1.56", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Atrial fibrillation", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "1.21", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Diabetes", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "1.20", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Cerebrovascular disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "1.33", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def card_collapse_utili_patient():
	return dbc.Card(
			[
				dbc.Row([
					dbc.Col("Comorbidity Type", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col("Trend", style={"font-family":"NotoSans-Regular","font-size":"1rem"})
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("No-Comorbidity", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "6%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Hypertension", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "8%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Coronary heart disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "8%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Chronic pulmonary disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "4%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Renal disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "9%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Atrial fibrillation", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "6%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Diabetes", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "4%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Cerebrovascular disease", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "7%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
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
					dbc.Col(dbc.Input(value = "5%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 2", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "12%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 3", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "23%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 4", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "41%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 5", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "68%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 6", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 7", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 8", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 9", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 10", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 11", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Month 12", style={"font-family":"NotoSans-Regular","font-size":"0.8rem"}),
					dbc.Col(dbc.Input(value = "100%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
			], style={"font-family":"NotoSans-Regular","font-size":"1rem", "padding-left":"1rem", "padding-right":"1rem"}
		)

def download_template():
	return html.A(
                            children=dbc.Button(
                                "Download the template file",
                                id='download-template',
                                color= 'link',
                            ),
                            href=os.path.join('data', 'setup.csv'),
                            download="setup.csv"
                        )