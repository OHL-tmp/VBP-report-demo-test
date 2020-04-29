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
		dbc.Button("Input & Edit Assumption", id = 'button-edit-assumption', style={"border-radius":"5rem"}),
                                dbc.Modal([
                                    dbc.ModalHeader(html.H1("Input & Edit Assumption", style={"font-family":"NotoSans-Black","font-size":"1.5rem"})),
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
		dbc.ListGroupItem([html.H4("CLient Input Assumptions")]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Plan Information", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Plan Type", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "MAPD", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Total Members", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "150,000", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
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
					dbc.Col("Copayment for Entresto by Channel and Days of Supply", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
				]),
			]),
		dbc.ListGroupItem([
			dbc.ListGroupItemHeading("Drug Information", style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem"}),
			dbc.ListGroupItemText([
				dbc.Row([
					dbc.Col("Entresto Pricing Information", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "$9.6 / unit (tablet)", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Assumptions for Each Measure", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(html.A('Download the template file'), style={"font-family":"NotoSans-Regular","font-size":"1rem","text-decoration":"underline","color":"#1357DD"}),
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
					dbc.Col("CHF Comorbidity Condition %CHF Comorbidity Condition %", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
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
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Total Cost PPPY by Patient Cohort", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),


				dbc.Row([
					dbc.Col("CHF Patient Cost Trend Assumptions", style={"font-family":"NotoSans-Regular","font-size":"1.2rem"}),
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual PPPY Cost Trend Before Taking Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "7%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual PPPY Cost Trend by Service Category", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual PPPY Cost Trend by Patient Cohort", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),


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
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Total Inpatient Admissions PPPY by Patient Cohort", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),


				dbc.Row([
					dbc.Col("CHF Patient Utilization Trend Assumptions", style={"font-family":"NotoSans-Regular","font-size":"1.2rem"}),
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual PPPY Inpatient Utilization Trend Before Taking Entresto", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "5.4%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Annual PPPY Inpatient Utilization Trend by Patient Cohort", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),

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
					dbc.Col(dbc.Button("···", size="sm", color='primary', style={"border-radius":"10rem"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Average Entresto Script PPPY (Per Patient Per Year)", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "6.9%", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				dbc.Row([
					dbc.Col("Average Units/ Script", style={"font-family":"NotoSans-Regular","font-size":"1rem"}),
					dbc.Col(dbc.Input(value = "70", bs_size="sm", style={"border-radius":"5rem","padding-left":"1rem","padding-right":"1rem","color":"#000","font-family":"NotoSans-Regular"}))
					], style={"padding-top":"1rem"}),
				]),
			]),
		],
		style={"border-radius":"0.5rem"})





