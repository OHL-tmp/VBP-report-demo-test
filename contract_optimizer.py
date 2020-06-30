#!/usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import base64
import datetime
import io

import pandas as pd
import numpy as np
import json

import pathlib
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State

from utils import *
from figure import *

from modal_simulation_measure_selection import *
from contract_calculation import *
from modal_simulation_input import *
from modal_simulation_realtime_assump import *
from model_simulation import *

from app import app

#app = dash.Dash(__name__, url_base_pathname='/vbc-demo/launch/')

#server = app.server


df_setup1=pd.read_csv("data/setup_1.csv")
df_setup2=pd.read_csv("data/setup_2.csv")
df_initial=df_setup1[df_setup1['id'].isin([0,1,2,9,11])]
## 初始化
global measures_select,df_setup_filter,dropdown_cohort,cohort_now

dropdown_cohort = 'CHF+AF'
cohort_now='CHF+AF'

df_setup_filter=pd.read_csv('data/setup_1.csv')
measures_select=['Cost & Utilization Reduction', 'Improving Disease Outcome', 'CHF Related Average Cost per Patient', 'CHF Related Hospitalization Rate', 'NT-proBNP Change %', 'LVEF LS Mean Change %']
domain_index=[0,3]
domain1_index=[1,2]
domain2_index=[4]
domain3_index=[]
domain4_index=[]
domain5_index=[]
list_forborder=[[0, True], [0, False], [1, True], [1, False], [2, True], [2, False], [3, True], [3, False], [4, True], [4, False]]
percent_list=[2,4,7,8,10,11,12,13,14,15,16,17,18,20,21,23,24,25,27,28,29]
dollar_list=[1,3,5,6]

df_factor_doc=pd.read_csv("data/confounding_factors_doc.csv")


#modebar display
button_to_rm=['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'hoverClosestCartesian','hoverCompareCartesian','hoverClosestGl2d', 'hoverClosestPie', 'toggleHover','toggleSpikelines']


#df_recom_measure = pd.read_csv("data/recom_measure.csv")
df_payor_contract_baseline = pd.read_csv("data/payor_contract_baseline.csv")
df_performance_assumption = pd.read_csv("data/performance_assumption.csv")


positive_measure = ["LVEF LS Mean Change %", "Change in Self-Care Score", "Change in Mobility Score", "DOT", "PDC", "MPR" ]

def create_layout(app):
#    load_data()
	return html.Div(
				[ 
					html.Div([Header_contract(app, True, False, False, False)], style={"height":"6rem"}, className = "sticky-top navbar-expand-lg"),
					html.A(id="top"),
					html.Div(
						[
							dbc.Tabs(
								[
									dbc.Tab(tab_setup(app), label="Contract Simulation Setup", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
									dbc.Tab(tab_result(app), label="Result", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
									
								], id = 'tab_container'
							),
							html.Div(default_temp_data(),id = 'temp-data',  style = {'display':'none'})
						],
						className="mb-3",
						style={"padding-left":"3rem", "padding-right":"3rem"},
					),
					
				],
				style={"background-color":"#f5f5f5"},
			)

def default_temp_data():
	t1 = pd.read_csv('data/performance_assumption.csv')
	t2 = pd.read_csv('data/recom_measure.csv')
	t3 = 'CHF+AF'
	t4 = ['CHF Related Average Cost per Patient', 'CHF Related Hospitalization Rate', 'LVEF LS Mean Change %']
	t5 = ['CHF Related Hospitalization Rate', 'LVEF LS Mean Change %']
	t6 = df_setup2
	t7 = df_setup1


	result = {'df_perfom_assump': t1.to_dict(), 'df_recom_measure': t2.to_dict(), 'recom_cohort':t3, 'meas_recom':t4, 'meas_recom_not':t5, 'setup_all':t6.to_dict(),  'setup_af':t7.to_dict()}
	
	with open('configure/optimizer_input.json','w') as outfile:
		json.dump(result, outfile)

	return [json.dumps(result)]

def table_setup(df_dict,cohort):
	global df_setup_filter,domain_index,domain1_index,domain2_index,domain3_index,domain4_index,domain5_index,dropdown_cohort,cohort_now

	
	if cohort==df_dict['cohort']:
		dff=pd.DataFrame(df_dict['data'])


		
	else:
		dff=df[df['measures']=='1'].copy()
		
		for i in range(len(df)):
			
			if df.values[i,0] in df_setup_filter['measures'].tolist():
			   
				dff.loc[i]=df_setup_filter[df_setup_filter['measures']==df.values[i,0]].iloc[0,:].tolist()            
			else:
				dff.loc[i]=df.iloc[i,:].tolist()
		
		k=0
		for i in domain_index:
			k=k+1
			weight_str=dff['weight_user'].iloc[eval('domain'+str(k)+'_index')]
			weight=[int(i.replace('$','').replace('%','').replace(',','')) for i in weight_str ]
			dff['weight_user'][i]=str(sum(weight))+'%'
			weight2_str=dff['weight_recom'].iloc[eval('domain'+str(k)+'_index')]
			weight2=[int(i.replace('$','').replace('%','').replace(',','')) for i in weight2_str ]
			dff['weight_recom'][i]=str(sum(weight2))+'%'
		
     
	table=dash_table.DataTable(
		data=dff.to_dict('records'),
		id='computed-table',
		columns=[
		{"name": '', "id":'measures'} ,
		{"name": '', "id":'recom_value'} ,
		{"name": 'Recommended', "id":'tarrecom_value'} ,
		{"name": 'User Defined', "id":'taruser_value', 'editable':True,} ,
		{"name": 'Recommended', "id":'probrecom'} ,
		{"name": 'User Defined', "id":'probuser'} ,
		{"name": 'Recommended', "id":'weight_recom'} ,
		{"name": 'User Defined', "id":'weight_user', 'editable':True,} , 
		{"name": 'highlight_recom', "id":'highlight_recom'} ,
		{"name": 'highlight_user', "id":'highlight_user'} ,
		{"name": 'green_thres', "id":'green_thres'} ,
		{"name": 'yellow_thres', "id":'yellow_thres'} ,
		{"name": 'id', "id":'id'} ,
		], 
		#row_selectable='multi',        
		

		style_data_conditional=[
			{ 'if': {'row_index':c[0],'column_editable': c[1] }, 
			 'color': 'grey', 
			 'backgroundColor': 'white',
			 'font-family': 'NotoSans-Regular',
			 'font-size':'0.8rem',
			 'font-weight':'bold',
			 'text-align':'start',
			 'border':'0px',
			 'border-bottom': '1px solid grey',
			 'border-top': '1px solid grey',
			 #'border-right': '0px',
	 
			  } if (c[0] in domain_index) and (c[1]==False) else 
			{ 'if': {'row_index':c[0] ,'column_editable': c[1],},
			 'color': 'grey', 
			 'font-family': 'NotoSans-Regular',
			 'font-size':'0.8rem',
			 'font-weight':'bold',
			 'text-align':'start',   
			 'border-bottom': '1px solid blue', 
			 'border-top': '1px solid grey', 
			 #'border-right': '0px',    
			  } if (c[0] in domain_index) and (c[1]==True) else 
			{
			'if': {'row_index':c[0] ,'column_editable': c[1], },
			'border': '1px solid blue',
			} if not(c[0] in domain_index) and (c[1]==True) else 
			{ 'if': {'row_index':c[0] ,'column_editable': c[1],},   
			 'border': '0px',       
			 #'border-right': '0px',    
			  }
			for c in list_forborder
		
	]+[{
			'if': {
				'column_id': 'probrecom',
				'filter_query': '{highlight_recom} eq "green"'
			},
			'backgroundColor': 'green',
			'color': 'white',
		},
		{
			'if': {
				'column_id': 'probrecom',
				'filter_query': '{highlight_recom} eq "yellow"'
			},
			'backgroundColor': '#f5b111',
			'color': 'black',
		},
		{
			'if': {
				'column_id': 'probrecom',
				'filter_query': '{highlight_recom} eq "red"'
			},
			'backgroundColor': 'red',
			'color': 'white',
		},
			{
			'if': {
				'column_id': 'probuser',
				'filter_query': '{highlight_user} eq "green"'
			},
			'backgroundColor': 'green',
			'color': 'white',
		},
		{
			'if': {
				'column_id': 'probuser',
				'filter_query': '{highlight_user} eq "yellow"'
			},
			'backgroundColor': '#f5b111',
			'color': 'black',
		},
		{
			'if': {
				'column_id': 'probuser',
				'filter_query': '{highlight_user} eq "red"'
			},
			'backgroundColor': 'red',
			'color': 'white',
		},
	
	],
		style_cell={
			'textAlign': 'center',
			'font-family':'NotoSans-Regular',
			'fontSize':12,
			'border':'0px',
			'height': '1.5rem',
		},
		style_cell_conditional=[
			
		{
			'if': {
				'column_id': 'recom_value',
			},
			'backgroundColor': '#bfbfbf',
			'color': 'black',
		},
		{
			'if': {
				'column_id': 'tarrecom_value',
			},
			'backgroundColor': '#bfbfbf',
			'color': 'black',
		},
		{
			'if': {
				'column_id': 'weight_recom',
			},
			'backgroundColor': '#bfbfbf',
			'color': 'black',
		},
			
		
		{
			'if': {
				'column_id': 'highlight_recom',
			},
			'display':'none'
		},
		{
			'if': {
				'column_id': 'highlight_user',
			},
			'display':'none'
		},
		{
			'if': {
				'column_id': 'green_thres',
			},
			'display':'none'
		},
		{
			'if': {
				'column_id': 'yellow_thres',
			},
			'display':'none'
		}, 
		{
			'if': {
				'column_id': 'id',
			},
			'display':'none'
		}, 
		],
		style_table={
			'back':  colors['blue'],
		},
		style_header={
			'height': '2.5rem',
			'minWidth': '3rem',
			'maxWidth':'3rem',
			'whiteSpace': 'normal',
			'backgroundColor': '#f1f6ff',
			'fontWeight': 'bold',
			'font-family':'NotoSans-CondensedLight',
			'fontSize':14,
			'color': '#1357DD',
			'text-align':'center',
			'border':'0px solid grey',
			'text-decoration':'none'
		},
		persistence = True,
		persistence_type = 'session',
				
	)
	return table 

def tab_setup(app):
	return html.Div(
				[
					dbc.Row(
						[
							dbc.Col(html.H1("Contract Simulation Setup", style={"padding-left":"2rem","font-size":"3"}), width=8),
							dbc.Col([
								modal_simulation_input()
								], 
								width=2,
								style={"padtop":"1rem"}),
							dbc.Col([
								modal_simulation_assump()
								], 
								width=2,
								style={"padtop":"1rem"}),
						],
						style={"padding-top":"2rem"}
					),
					html.Div(
						[
							dbc.Row(
								[
									dbc.Col(html.H1("Performance Measure Setup", style={"color":"#f0a800", "font-size":"1rem","padding-top":"0.8rem"}), width=9),
									
								]
							)
						],
						style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#fff","margin-top":"2rem"}
					),
					html.Div(
						[
							card_performance_measure_setup(app),
						]
					),
					html.Div(
						[
							dbc.Row(
								[
									dbc.Col(html.H1("Contractual Arrangement Setup", style={"color":"#f0a800", "font-size":"1rem","padding-top":"0.8rem"}), width=9),
									
								]
							)
						],
						style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#fff","margin-top":"2rem"}
					),
					html.Div(
						[
							card_contractural_arrangement_setup(app),
						]
					),
					html.Div([
						dbc.Button(
							"Submit for Simulation", 
							color="primary",
							id = 'button-simulation-submit', 
							href='#top',
							style={"border-radius":"10rem","box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)"}
						)
						],
						style={"text-align":"center", "padding-bottom":"2rem"}),

					
				]
			)


def card_performance_measure_setup(app):
	return dbc.Card(
				dbc.CardBody(
					[
						card_target_patient(app),
						card_outcome_measure(app),
						card_overall_likelihood_to_achieve(app),
					]
				),
				className="mb-3",
				style={"background-color":"#fff", "border":"none", "border-radius":"0.5rem"}
			)

def card_target_patient(app):
	return dbc.Card(
				dbc.CardBody(
					[
						dbc.Row(
							[
								dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
								dbc.Col(html.H4("Patient Cohort Setup", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
							],
							no_gutters=True,
						),
						dbc.Row(
							[
								dbc.Col(
									[
										html.Div([
											html.H3("Recommended", style={"font-size":"1rem"}),
											html.H5("CHF+AF (Recommended)", style={"font-size":"1rem"}, id = 'target-patient-recom'),
										], hidden = True),
									],
									style={"padding":"0.8rem"},
									width=4,
								),
								dbc.Col(
									[
										html.H3("Select Patient Cohort", style={"font-size":"1rem"}),
										html.Div([
											dcc.Dropdown(
												id = 'target-patient-input',
												options = [{'label':'CHF+AF (Recommended)', 'value':'CHF+AF'},
															{'label':'All CHF Patients', 'value':'All CHF Patients'}],
												value = 'CHF+AF',
												persistence = True,
												persistence_type = 'session',
												style={"font-family":"NotoSans-Regular"}
											)
										]),
									], 
									style={"padding":"0.8rem"},
									width=4,
								),
							],
							style={"padding-left":"1.5rem"}
						),
						
					]
				),
				className="mb-3",
				style={"background-color":"#f7f7f7", "border":"none", "border-radius":"0.5rem"}
			)


def card_outcome_measure(app):
	return dbc.Card(
				dbc.CardBody(
					[
						dbc.Row(
							[
								dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
								dbc.Col(
									[
										html.H4(
											[
												"Value Based Measure ",
												html.Span(
													"\u24D8",
													style={"font-size":"0.8rem"}
												)
											],
											id="tooltip-vbc-measure",
											style={"font-size":"1rem", "margin-left":"10px"}
										),
										dbc.Tooltip(
											"Value based measures are recommended based on each measure’s stability, improvement level from baseline, data availability and ease to implement or monitor, efficacy results from clinical trials, payer’s acceptance level, pharma’s preference, etc.",
											target="tooltip-vbc-measure",
											style={"text-align":"start"}
										),
									],
									
									width="auto"
								),
							],
							no_gutters=True,
						),
						
						dbc.Row(
							[
								dbc.Col(
#                                   dbc.Button("Edit Assumption"),
									modal_optimizer_domain_selection(domain_ct),
									style={"padding-left":"2rem","text-align":"center"},
									width=5,
								),
								dbc.Col(
									[
										html.Div(
											[
												html.H4("Baseline", style={"font-size":"1rem"}),
												html.Hr(className="ml-1"),
												
											]
										)
									],
									style={"text-align":"center"},
									width=1,
								),
								dbc.Col(
									[
										html.Div(
											[
												html.Div(
													[
														html.H4(
															[
																"Target ",
																html.Span(
																	"\u24D8",
																	style={"font-size":"0.8rem"}
																)
															],
															id="tooltip-vbc-target",
															style={"font-size":"1rem"}
														),
														dbc.Tooltip(
															"Most conservative value within high likelihood band for client to achieve",
															target="tooltip-vbc-target",
															style={"text-align":"start"}
														),
													],
												),
												html.Hr(className="ml-1"),
												
											]
										)
									],
									style={"text-align":"center"},
									width=2,
								),
								dbc.Col(
									[
										html.Div(
											[
												html.Div(
													[
														html.H4(
															[
																"Likelihood to achieve ",
																html.Span(
																	"\u24D8",
																	style={"font-size":"0.8rem"}
																)
															],
															id="tooltip-vbc-achieve",
															style={"font-size":"1rem"}
														),
														dbc.Tooltip(
															"Defined by predetermined probability threshold, which can be customized",
															target="tooltip-vbc-achieve",
															style={"text-align":"start"}
														),
													],
												),
												html.Hr(className="ml-1"),
												
											]
										)
									],
									style={"text-align":"center"},
									width=2,
								),
								dbc.Col(
									[
										html.Div(
											[
												html.Div(
													[
														html.H4(
															[
																"Weight ",
																html.Span(
																	"\u24D8",
																	style={"font-size":"0.8rem"}
																)
															],
															id="tooltip-vbc-weight",
															style={"font-size":"1rem"}
														),
														dbc.Tooltip(
															"Recommended weights are assigned based on each measure’s stability (i.e., higher weight is assigned more stable measures)",
															target="tooltip-vbc-weight",
															style={"text-align":"start"}
														),
													],
												),
												html.Hr(className="ml-1"),
												
											]
										)
									],
									style={"text-align":"center"},
									width=2,
								),

							],
							style={"padding-right":"0rem", "padding-left":"0rem", "width":"105%", "margin-left":"-4rem", "margin-bottom":"-1rem"}
							
						),
#                        card_measure_modifier(domain_ct),
#                        card_measure_modifier(),
#,[0,1,2,9,11]
						html.Div([table_setup({'cohort': 'CHF+AF', 'data': df_initial.to_dict()},'CHF+AF')],id='table_setup'),
						html.Div(html.H6("\u29bf Hospitalization rate is on per 1,000 patient basis"))
					]
				),
				className="mb-3",
				style={"background-color":"#f7f7f7", "border":"none", "border-radius":"0.5rem"}
			)


def card_measure_modifier(n):
	card_outcome_domain_container = []
	for i in range(n):
		card = html.Div(
					[
						dbc.Card(
							dbc.CardBody(
								[
									dbc.Row(
										[
											dbc.Col(domain_set[i], id = u'outcome-domain-{}'.format(i+1), style={"font-family":"NotoSans-Regular","color":"#919191","font-size":"1rem"}, width=10),
											dbc.Col(id = u'outcome-domain-weight-recom-{}'.format(i+1), style={"font-family":"NotoSans-Regular","color":"#919191","font-size":"1rem"}),
											dbc.Col(id = u'outcome-domain-weight-user-{}'.format(i+1), style={"font-family":"NotoSans-Regular","color":"#919191","font-size":"1rem"}),
										]
									),
									html.Hr(className="ml-1"),
									row_measure_modifier_combine(i),
								]
							),
						),
					], 
					id = u'outcome-domain-container-{}'.format(i+1),
					hidden = True
				)

		card_outcome_domain_container.append(card)

	return html.Div(card_outcome_domain_container)


def row_measure_modifier_combine(n):
	card_outcome_measure_container = []
	measures_lv1 = Domain_options[domain_focus[n]]
	key = list(measures_lv1.keys())
	measures_lv2 = []
	for i in range(len(key)):
		for k in measures_lv1[key[i]]:
			measures_lv2 = measures_lv2 + [k]
	for m in range(len(measures_lv2)):
		recom_weight = df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Weight']
		if len(recom_weight) >0:
			recom_weight_pct = '{:.0%}'.format(recom_weight.values[0])
		else:
			recom_weight_pct = ""
		if m in dollar_input:
			card = html.Div([
				dbc.Row(
					[
						dbc.Col(html.Div(measures_lv2[m]), width=4),
						dbc.Col(html.Div('$'+str(df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Baseline']), id = u'measure-base-recom-{}-{}'.format(n+1, m+1)), width=0.5),
						dbc.Col(html.Div('$'+str(df_payor_contract_baseline[df_payor_contract_baseline['Measure'] == measures_lv2[m]]['Baseline']), id = u'measure-base-user-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(html.Div('$'+str(df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Target']), id = u'measure-target-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(
							dcc.Input(id = u'measure-target-user-{}-{}'.format(n+1, m+1), 
								type = 'number', debounce = True, persistence = True, persistence_type = 'session', size="4"), 
							width=1),
						dbc.Col(html.Div(df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Likelihood'], id = u'measure-like-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(html.Div(id = u'measure-like-user-{}-{}'.format(n+1, m+1),style = {"background-color": '#ffffff'}), width=1),
						dbc.Col(html.Div(recom_weight_pct, id = u'measure-weight-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(
							dcc.Input(id = u'measure-weight-user-{}-{}'.format(n+1, m+1),
								type = 'number', debounce = True, persistence = True, persistence_type = 'session',
								min = 0, max = 100, size="4"), 
							width=1),
					]
				)
				],
				style={"font-family":"NotoSans-Regular","font-size":"1rem"}, 
				id = u"outcome-measure-row-{}-{}".format(n+1,m+1))
		elif m in percent_input:
			card = html.Div([
				dbc.Row(
					[
						dbc.Col(html.Div(measures_lv2[m]), width=4),
						dbc.Col(html.Div('{:.0%}'.format(df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Baseline']), id = u'measure-base-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(html.Div('{:.0%}'.format(df_payor_contract_baseline[df_payor_contract_baseline['Measure'] == measures_lv2[m]]['Baseline']), id = u'measure-base-user-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(html.Div('{:.0%}'.format(df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Target']), id = u'measure-target-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(
							dcc.Input(id = u'measure-target-user-{}-{}'.format(n+1, m+1), 
								type = 'number', debounce = True, persistence = True, persistence_type = 'session',
								min = 0, max = 100, size="4"), 
							width=1),
						dbc.Col(html.Div(df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Likelihood'], id = u'measure-like-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(html.Div(id = u'measure-like-user-{}-{}'.format(n+1, m+1),style = {"background-color": '#ffffff'}), width=1),
						dbc.Col(html.Div(recom_weight_pct, id = u'measure-weight-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(
							dcc.Input(id = u'measure-weight-user-{}-{}'.format(n+1, m+1),
								type = 'number', debounce = True, persistence = True, persistence_type = 'session',
								min = 0, max = 100, size="4"), 
							width=1),
					]
				)
				],
				style={"font-family":"NotoSans-Regular","font-size":"1rem"}, 
				id = u"outcome-measure-row-{}-{}".format(n+1,m+1))
		else:
			card = html.Div([
	#            row_measure_modifier(measures_lv2[m])
				dbc.Row(
					[
						dbc.Col(html.Div(measures_lv2[m], id = 'measure-name-{}-{}'.format(n+1, m+1)), width=4),
						dbc.Col(html.Div(df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Baseline'], id = u'measure-base-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(html.Div(df_payor_contract_baseline[df_payor_contract_baseline['Measure'] == measures_lv2[m]]['Baseline'], id = u'measure-base-user-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(html.Div(df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Target'], id = u'measure-target-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(
							dcc.Input(id = u'measure-target-user-{}-{}'.format(n+1, m+1), 
								type = 'number', debounce = True, persistence = True, persistence_type = 'session', size="4"), 
							width=1),
						dbc.Col(html.Div(df_recom_measure[df_recom_measure['Measure'] == measures_lv2[m]]['Likelihood'], id = u'measure-like-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(html.Div(id = u'measure-like-user-{}-{}'.format(n+1, m+1),style = {"background-color": '#ffffff'}), width=1),
						dbc.Col(html.Div(recom_weight_pct, id = u'measure-weight-recom-{}-{}'.format(n+1, m+1)), width=1),
						dbc.Col(
							dcc.Input(id = u'measure-weight-user-{}-{}'.format(n+1, m+1),
								type = 'number', debounce = True, persistence = True, persistence_type = 'session',
								min = 0, max = 100, size="4"), 
							width=1),
					]
				)
				], 
				style={"font-family":"NotoSans-Regular","font-size":"1rem"}, 
				id = u"outcome-measure-row-{}-{}".format(n+1,m+1))
		card_outcome_measure_container.append(card)
	return html.Div(card_outcome_measure_container)




def card_overall_likelihood_to_achieve(app):
	return dbc.Card(
				dbc.CardBody(
					[
						dbc.Row(
							[
								dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
								dbc.Col(html.H4("Overall likelihood to achieve", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
								dbc.Col(html.Div('High'), width=1),
								dbc.Col(html.Div(id = 'overall-like-user'), width=1),
								dbc.Col(html.Div(""), width=2),
							],
							no_gutters=True,
						),
						
					]
				),
				className="mb-3",
				style={"background-color":"#f7f7f7", "border":"none", "border-radius":"0.5rem"}
			)


def card_contractural_arrangement_setup(app):
	return dbc.Card(
				dbc.CardBody(
					[
						card_contract_wo_vbc_adjustment(app),
						card_vbc_contract(app),
						card_contract_adjust(app),
					]
				),
				className="mb-3",
				style={"border":"none", "border-radius":"0.5rem"}
			)

def card_contract_wo_vbc_adjustment(app):
	return dbc.Card(
				dbc.CardBody(
					[
						dbc.Row(
							[
								dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
								dbc.Col(html.H4("Contract without VBC Adjustment", style={"font-size":"1rem", "margin-left":"10px"}), width=5),
								dbc.Col(html.Div("Rebate", style={"font-family":"NotoSans-Condensed","font-size":"1rem","text-align":"center"}), width=1),
								dbc.Col(
									dbc.InputGroup(
												[
													 dcc.Input(id = 'input-rebate',
																type = 'number', debounce = True, persistence = True, persistence_type = 'session', value = 40, 
																min = 0, max = 100, size="13", style={"text-align":"center"},
																disabled = True), 
													dbc.InputGroupAddon("%", addon_type="append"),
												],
												className="mb-3",
												size="sm"
											),
									width=2
								),
								dbc.Col([
									dbc.Button("Volumn Based Rebate", id = 'button-edit-rebate-1', style={"background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Regular", "font-size":"0.6rem"}),
									dbc.Modal([
										dbc.ModalHeader(html.H1("EDIT Rebate Input", style={"font-size":"1rem"})),
										dbc.ModalBody([
											dbc.Row([
												dbc.Col("% of market share range"),
												dbc.Col("Rebate %"),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-l-1',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'novbc-r-1',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-p-1',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-l-2',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'novbc-r-2',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-p-2', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-l-3',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'novbc-r-3',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-p-3',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-l-4', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'novbc-r-4', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-p-4',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-l-5',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'novbc-r-5',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'novbc-p-5',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
#                                           dbc.Row([
#                                               dbc.Col(html.H4("+ Add another range", style={"font-size":"0.8rem","color":"#1357DD"}), ),
#                                               ],
#                                               style={"padding":"1rem"}),
											]),
										dbc.ModalFooter(
											dbc.Button('CLOSE', id = 'close-edit-rebate-1', size="sm")
											)
										], id = 'modal-edit-rebate-1', backdrop = 'static', size = 'lg'),
									], width=2
								),
							],
							no_gutters=True,
						),
						
					]
				),
				className="mb-3",
				style={"background-color":"#f7f7f7", "border":"none", "border-radius":"0.5rem"}
			)

def card_vbc_contract(app):
	return dbc.Card(
				dbc.CardBody(
					[
						dbc.Row(
							[
								dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
								dbc.Col(html.H4("VBC Contract", style={"font-size":"1rem", "margin-left":"10px"}), width=3),
								dbc.Col(
									html.Div(
										[
											html.Div("Base Rebate", style={"font-family":"NotoSans-Condensed","font-size":"1rem","text-align":"start"}),
											dbc.InputGroup(
												[
													dcc.Input(id = 'input-base-rebate',
														type = 'number', debounce = True, persistence = True, persistence_type = 'session', value = 40,
														min = 0, max = 100, size="13",style={"text-align":"center"}, disabled = True), 
													dbc.InputGroupAddon("%", addon_type="append"),
												],
												className="mb-3",
												size="sm"
											),

										]
									),
									width=2
								),

								dbc.Col([
									dbc.Button("Volumn Based Rebate", id = 'button-edit-rebate-2', style={"background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Regular", "font-size":"0.6rem"}),
									dbc.Modal([
										dbc.ModalHeader(html.H1("Edit Rebate Input", style={"font-size":"1rem"})),
										dbc.ModalBody([
											dbc.Row([
												dbc.Col("% of market share range"),
												dbc.Col("Rebate %"),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-l-1', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'vbc-r-1',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-p-1',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-l-2', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'vbc-r-2',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-p-2', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-l-3',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'vbc-r-3',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-p-3',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-l-4', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'vbc-r-4', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-p-4', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-l-5',type = 'number', disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(id = 'vbc-r-5', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(id = 'vbc-p-5', type = 'number',disabled = True),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
#                                           dbc.Row([
#                                               dbc.Col(html.H4("+ Add another range", style={"font-size":"0.8rem","color":"#1357DD"})),
#                                               ],
#                                               style={"padding":"1rem"}),
											]),
										dbc.ModalFooter(
											dbc.Button('CLOSE', id = 'close-edit-rebate-2', size="sm")
											)
										], id = 'modal-edit-rebate-2', backdrop = 'static', size = 'lg'),
									], width=2
								),

								dbc.Col(
									html.Div(
										[
											html.Div("VBC Adjustment Method", style={"font-family":"NotoSans-Condensed","font-size":"1rem","text-align":"start"}),
											dcc.Dropdown(
												options = [
																{'label':'Rebate adjustment', 'value':'Rebate adjustment'}
															],
												value = 'Rebate adjustment',
												style={"font-family":"NotoSans-Regular","font-size":"0.8rem","width":"11rem"}
											)
												
										]
									),
									width=3
								),
									
#                               dbc.Col(html.Div("Maximum Positive Adjustment"), width=1),


							],
							no_gutters=True,
						),
					]
				),
				className="mb-3",
				style={"background-color":"#f7f7f7", "border":"none", "border-radius":"0.5rem"}
			)

def card_contract_adjust(app):
	return dbc.Card(
				dbc.CardBody(
					[
						dbc.Row(
							[
								dbc.Col(html.Img(src=app.get_asset_url("simulation_illustration.png"), style={"max-width":"100%","max-height":"100%"}), width=6),
								dbc.Col(card_contract_adjust_sub(app), width=6)
							],
							no_gutters=True,
						),
					]
				),
				className="mb-3",
				style={"background-color":"#f7f7f7", "border":"none", "border-radius":"0.5rem"}
			)


def card_contract_adjust_sub(app):
	return dbc.Card(
				dbc.CardBody(
					[
						dbc.Col(html.H1("Positive Adjustment", style={"font-size":"1rem", "padding-bottom":"1rem"})),
						dbc.Row(
							[
								dbc.Col(html.Div(""), width=6),
								dbc.Col(html.H3("Recommended", style={"font-size":"0.8rem"}), width=3),
								dbc.Col(html.H3("User Defined", style={"font-size":"0.8rem"}), width=3),
							],
							no_gutters=True,
						),
						dbc.Row(
							[
								dbc.Col(html.H3("\u2460 Performance Threshold", style={"color":"#919191","font-size":"1rem"}), width=6),
								dbc.Col(html.Div("120%", id = 'recom-pos-perf', style={"font-family":"NotoSans-Regular","font-size":"1rem", "text-align":"center"}), width=3),
								dbc.Col(
									dbc.InputGroup(
										[
											dcc.Input(id = 'input-pos-perform',
												type = 'number', debounce = True, persistence = True, persistence_type = 'session',
												min = 100, size="6",style={"text-align":"center"}), 
											dbc.InputGroupAddon("%", addon_type="append"),
										],
										className="mb-3",
										size="sm"
									),
									width=3,
									style={"text-align":"end"}
								),

							],
							no_gutters=True,
						),
						dbc.Row(
							[
								dbc.Col(html.H3("\u2461 Rebate Adjustment Cap", style={"color":"#919191","font-size":"1rem"}), width=6),
								dbc.Col(
									dbc.InputGroup(
										[
											dcc.Input(id = 'input-max-pos-adj',
												type = 'number', debounce = True, persistence = True, persistence_type = 'session',
												min = 0, max = 100, size="30", style={"text-align":"center"}), 
											dbc.InputGroupAddon("%", addon_type="append"),
										],
										className="mb-3",
										size="sm"
									),
									width=6,
									style={"text-align":"end"}
								),
								# dbc.Col(
								# 	dbc.InputGroup(
								# 		[
								# 			dcc.Input(id = 'input-pos-adj',
								# 				type = 'number', debounce = True, persistence = True, persistence_type = 'session',
								# 				min = 0, size="6",style={"text-align":"center"}), 
								# 			dbc.InputGroupAddon("%", addon_type="append"),
								# 		],
								# 		className="mb-3",
								# 		size="sm"
								# 	),
								# 	width=3,
								# 	style={"text-align":"end"}
								# ),
								
							],
							no_gutters=True,
						),

						html.Hr(className="ml-1"),

						dbc.Col(html.H1("Negative Adjustment", style={"font-size":"1rem", "padding-bottom":"1rem"})),
						dbc.Row(
							[
								dbc.Col(html.Div(""), width=6),
								dbc.Col(html.H3("Recommended", style={"font-size":"0.8rem"}), width=3),
								dbc.Col(html.H3("User Defined", style={"font-size":"0.8rem"}), width=3),
							],
							no_gutters=True,
						),
						dbc.Row(
							[
								dbc.Col(
									html.Div(
										[
											html.H3(
												[
													"\u2462 Performance Threshold ",
													html.Span(
														"\u24D8",
														style={"font-size":"0.8rem"}
													)
												],
												id="tooltip-vbc-negperf",
												style={"color":"#919191", "font-size":"1rem"}
											),
											dbc.Tooltip(
												"Recommended performance threshold is determined at the level where the probability to hit maximum negative rebate adjustment is no greater than a predetermined threshold (can be customized)",
												target="tooltip-vbc-negperf",
												style={"text-align":"start"}
											),
										],
									),
									width=6
								),
								dbc.Col(html.Div("80%", id = 'recom-neg-perf', style={"font-family":"NotoSans-Regular","font-size":"1rem", "text-align":"center"}), width=3),
								dbc.Col(
									dbc.InputGroup(
										[
											dcc.Input(id = 'input-neg-perform',
													type = 'number', debounce = True, persistence = True, persistence_type = 'session',
													min = 0, max = 100, size="6",style={"text-align":"center"}), 
											dbc.InputGroupAddon("%", addon_type="append"),
										],
										className="mb-3",
										size="sm"
									),
									width=3,
									style={"text-align":"end"}
								),
							],
							no_gutters=True,
						),
						dbc.Row(
							[
								dbc.Col(html.H3("\u2463 Rebate Adjustment Cap", style={"color":"#919191","font-size":"1rem"}), width=6),
								dbc.Col(
									dbc.InputGroup(
										[
											dbc.InputGroupAddon("-", addon_type="prepend"),
											dcc.Input(id = 'input-max-neg-adj',
												type = 'number', debounce = True, persistence = True, persistence_type = 'session',
												min = 0, max = 100, size="27", style={"text-align":"center"}), 
											dbc.InputGroupAddon("%", addon_type="append"),
										],
										className="mb-3",
										size="sm"
									),
									width=6,
									style={"text-align":"end"}
								),
								# dbc.Col(
								# 	dbc.InputGroup(
								# 		[
								# 			dbc.InputGroupAddon("-", addon_type="prepend"),
								# 			dcc.Input(id = 'input-neg-adj',
								# 				type = 'number', debounce = True, persistence = True, persistence_type = 'session',
								# 				min = 0, max = 100, size="4",style={"text-align":"center"}), 
								# 			dbc.InputGroupAddon("%", addon_type="append"),
								# 		],
								# 		className="mb-3",
								# 		size="sm"
								# 	),
								# 	width=3,
								# 	style={"text-align":"end"}
								# ),
								
							],
							no_gutters=True,
						),
					]
				),
				className="mb-3",
				style={"background-color":"#f7f7f7", "border":"none", "border-radius":"0.5rem"}
			)


def tab_result(app):
	return html.Div(
				[
					dbc.Row(
						[
							dbc.Col(html.H1("Contract Simulation Result"), width=9),
							
						]
					),
					html.Div(
						[
							dbc.Button(
								"Pharma’s Revenue Projection",
								id="optimizer-collapse_button_result_1",
								className="mb-3",
								color="light",
								block=True,
								style={"font-family":"NotoSans-CondensedBlack","font-size":"1.5rem","border-radius":"0.5rem","border":"1px solid #1357DD","color":"#1357DD"}
							),
							dbc.Collapse(
								collapse_result_1(app),
								id="optimizer-collapse_result_1",
								is_open = True,
							),
						],
						style={"padding-top":"1rem"}
					),
					html.Div(
						[
							dbc.Button(
								"Pharma’s Rebate Projection",
								id="optimizer-collapse_button_result_2",
								className="mb-3",
								color="light",
								block=True,
								style={"font-family":"NotoSans-CondensedBlack","font-size":"1.5rem","border-radius":"0.5rem","border":"1px solid #1357DD","color":"#1357DD"}
							),
							dbc.Collapse(
								collapse_result_2(app),
								id="optimizer-collapse_result_2",
								#is_open = True,
							),
						],
						style={"padding-top":"1rem"}
					),
					html.Div(
						[
							dbc.Button(
								"Plan’s Total Cost Projection for Target Patient",
								id="optimizer-collapse_button_result_3",
								className="mb-3",
								color="light",
								block=True,
								style={"font-family":"NotoSans-CondensedBlack","font-size":"1.5rem","border-radius":"0.5rem","border":"1px solid #1357DD","color":"#1357DD"}
							),
							dbc.Collapse(
								collapse_result_3(app),
								id="optimizer-collapse_result_3",
								#is_open = True,
							),
						],
						style={"padding-top":"1rem"}
					),
					html.Div(
						[
							dbc.Button(
								"Confounding Factors Needed to be Accounted for in the Contract",
								id="optimizer-collapse_button_confounding_factors",
								className="mb-3",
								color="light",
								block=True,
								style={"font-family":"NotoSans-CondensedBlack","font-size":"1.5rem","border-radius":"0.5rem","border":"1px solid #1357DD","color":"#1357DD"}
							),
							dbc.Collapse(
								collapse_confounding_factors(app),
								id="optimizer-collapse_confounding_factors",
							),
						],
						style={"padding-top":"1rem"}
					),
					html.Div(
						[
							"",
						],
						style={"height":"2rem"}
					)
				],
				style={"padding-top":"2rem","padding-left":"1rem","padding-right":"1rem"}
			)



def collapse_result_1(app):
	return dbc.Card(
				dbc.CardBody(
					[
						html.Div(html.Img(src=app.get_asset_url("simulation_intro.png"), style={"max-width":"100%","max-height":"100%", "border-radius":"0.5rem","border":"1px dotted #919191"}), style={"height":"4rem"}),
						dbc.Row(
							[
								dbc.Col(html.Div(
									[
										dcc.Graph(id = 'sim_result_box_1',style={"height":"50vh", "width":"80vh"},config={'modeBarButtonsToRemove': button_to_rm,'displaylogo': False,})
									]
								),width=6 ),
								dbc.Col(html.Div(id = 'sim_result_table_1'), width=6)
							]
						)
					]
				),
				style={"border":"none","padding":"1rem"}
			)



def collapse_result_2(app):
	return dbc.Card(
				dbc.CardBody(
					[
						html.Div(html.Img(src=app.get_asset_url("simulation_intro2.png"), style={"max-width":"100%","max-height":"100%", "border-radius":"0.5rem","border":"1px dotted #919191"}), style={"height":"4rem"}),
						dbc.Row(
							[
								dbc.Col(html.Div([dcc.Graph(id = 'sim_result_box_2',style={"height":"50vh", "width":"80vh"},config={'modeBarButtonsToRemove': button_to_rm,'displaylogo': False,})]),width=6 ),
								dbc.Col(html.Div(id = 'sim_result_table_2'), width=6)
							]
						)
					]
				),
				style={"border":"none","padding":"1rem"}
			)



def collapse_result_3(app):
	return dbc.Card(
				dbc.CardBody(
					[
						html.Div(html.Img(src=app.get_asset_url("simulation_intro2.png"), style={"max-width":"100%","max-height":"100%", "border-radius":"0.5rem","border":"1px dotted #919191"}), style={"height":"4rem"}),
						dbc.Row(
							[
								dbc.Col(html.Div([dcc.Graph(id = 'sim_result_box_3',style={"height":"50vh", "width":"80vh"},config={'modeBarButtonsToRemove': button_to_rm,'displaylogo': False,})]),width=6 ),
								dbc.Col(html.Div(id = 'sim_result_table_3'), width=6)
							]
						)
					]
				),
				style={"border":"none","padding":"1rem"}
			)



def collapse_confounding_factors(app):
	return dbc.Card(
				dbc.CardBody(
					[
						dbc.Row(
							[
								dbc.Col(html.Div([table_factor_doc(df_factor_doc)], style={"width":"100%"}), width=12),
								#dbc.Col(html.Img(src=app.get_asset_url("logo-demo.png")), width=6)
							]
						)
					]
				),
				style={"border":"none","padding":"1rem"}
			)




layout = create_layout(app)


#app.layout = create_layout(app)


#realtime assump modal
@app.callback(
	Output('modal-edit-realtime-assumption','is_open'),
	[Input('button-edit-realtime-assumption','n_clicks'),
	Input('close-edit-realtime-assumption','n_clicks')],
	[State('modal-edit-realtime-assumption','is_open')]
	)
def open_modal(n1,n2,is_open):
	if n1 or n2:
		return not is_open
	else:
		return is_open

@app.callback(
	[Output('realtime-assump-input-utilizer', 'value'),
	Output('realtime-assump-input-script', 'value')],
	[Input('realtime-assump-dropdown-tier', 'value')]
	)
def tier_assump(t):
	if t == 1:
		return 10,0.86
	elif t == 2:
		return 8,0.83
	elif t == 3:
		return 7,0.8
	elif t == 4:
		return 6,0.74
	elif t == 5:
		return 5.5,0.7
	else:
		return "",""

@app.callback(
	Output('realtime-assump-button-collapse-rebatenovbc','disabled'),
	[Input('realtime-assump-input-rebatenovbc', 'value')]
	)
def disable_collapse(v):
	if v:
		return True
	else:
		return False

@app.callback(
	Output('realtime-assump-button-collapse-rebatevbc','disabled'),
	[Input('realtime-assump-input-rebatevbc', 'value')]
	)
def disable_collapse(v):
	if v:
		return True
	else:
		return False

@app.callback(
	Output('realtime-assump-input-rebatevbc', 'disabled'),
	[Input('vbc-l-1-input', 'value'),
	Input('vbc-r-1-input', 'value'),
	Input('vbc-p-1-input', 'value')]
	)
def disable_rebate(v1, v2, v3):
	if v1 or v2 or v3:
		return True
	else: 
		return False

@app.callback(
	Output('realtime-assump-input-rebatenovbc', 'disabled'),
	[Input('novbc-l-1-input', 'value'),
	Input('novbc-r-1-input', 'value'),
	Input('novbc-p-1-input', 'value')]
	)
def disable_rebate(v1, v2, v3):
	if v1 or v2 or v3:
		return True
	else: 
		return False

@app.callback(
	[Output('realtime-assump-collapse-rebatenovbc', 'is_open'),
	Output('realtime-assump-button-collapse-rebatenovbc', 'children')],
	[Input('realtime-assump-button-collapse-rebatenovbc', 'n_clicks')]
	)
def toggle_collapse(n):
	if n and n%2 == 1:
		return True, '\u25B2'
	return False, '\u25BC'

@app.callback(
	[Output('realtime-assump-collapse-rebatevbc', 'is_open'),
	Output('realtime-assump-button-collapse-rebatevbc', 'children')],
	[Input('realtime-assump-button-collapse-rebatevbc', 'n_clicks')]
	)
def toggle_collapse(n):
	if n and n%2 == 1:
		return True, '\u25B2'
	return False, '\u25BC'

@app.callback(
	[Output('realtime-assump-collapse-rampup', 'is_open'),
	Output('realtime-assump-button-collapse-rampup', 'children')],
	[Input('realtime-assump-button-collapse-rampup', 'n_clicks')]
	)
def toggle_collapse(n):
	if n and n%2 == 1:
		return True, '\u25B2'
	return False, '\u25BC'

@app.callback(
	[Output('realtime-assump-div-rebatenovbc-2', 'hidden'),
	Output('realtime-assump-div-rebatenovbc-3', 'hidden'),
	Output('realtime-assump-div-rebatenovbc-4', 'hidden'),
	Output('realtime-assump-div-rebatenovbc-5', 'hidden'),
	Output('realtime-assump-button-addrebatenovbc', 'disabled')],
	[Input('realtime-assump-button-addrebatenovbc', 'n_clicks')]
	)
def add_rebate_range(n):
	if n:
		if n == 1:
			return False, True, True, True, False
		elif n == 2:
			return False, False, True, True, False
		elif n == 3:
			return False, False, False, True, False
		else:
			return False, False, False, False, True
	else:
		return True, True, True, True, False

@app.callback(
	[Output('realtime-assump-div-rebatevbc-2', 'hidden'),
	Output('realtime-assump-div-rebatevbc-3', 'hidden'),
	Output('realtime-assump-div-rebatevbc-4', 'hidden'),
	Output('realtime-assump-div-rebatevbc-5', 'hidden'),
	Output('realtime-assump-button-addrebatevbc', 'disabled')],
	[Input('realtime-assump-button-addrebatevbc', 'n_clicks')]
	)
def add_rebate_range(n):
	if n:
		if n == 1:
			return False, True, True, True, False
		elif n == 2:
			return False, False, True, True, False
		elif n == 3:
			return False, False, False, True, False
		else:
			return False, False, False, False, True
	else:
		return True, True, True, True, False

@app.callback(
	[Output('input-rebate', 'value'),
	Output('input-base-rebate', 'value')],
	[Input('close-edit-realtime-assumption', 'n_clicks')],
	[State('realtime-assump-input-rebatenovbc', 'value'),
	State('realtime-assump-input-rebatevbc', 'value')]
	)
def update_rebate(n, v1, v2):
	return v1, v2

@app.callback(
	[Output(f'novbc-l-{i+1}', 'value') for i in range(5)]
	+[Output(f'novbc-r-{i+1}', 'value') for i in range(5)]
	+[Output(f'novbc-p-{i+1}', 'value') for i in range(5)],
	[Input('close-edit-realtime-assumption', 'n_clicks')],
	[State(f'novbc-l-{i+1}-input', 'value') for i in range(5)]
	+[State(f'novbc-r-{i+1}-input', 'value') for i in range(5)]
	+[State(f'novbc-p-{i+1}-input', 'value') for i in range(5)]
	)
def update_rebate_range(n, l1,l2,l3,l4,l5, r1,r2,r3,r4,r5, p1,p2,p3,p4,p5):
	return l1,l2,l3,l4,l5, r1,r2,r3,r4,r5, p1,p2,p3,p4,p5

@app.callback(
	[Output(f'vbc-l-{i+1}', 'value') for i in range(5)]
	+[Output(f'vbc-r-{i+1}', 'value') for i in range(5)]
	+[Output(f'vbc-p-{i+1}', 'value') for i in range(5)],
	[Input('close-edit-realtime-assumption', 'n_clicks')],
	[State(f'vbc-l-{i+1}-input', 'value') for i in range(5)]
	+[State(f'vbc-r-{i+1}-input', 'value') for i in range(5)]
	+[State(f'vbc-p-{i+1}-input', 'value') for i in range(5)]
	)
def update_rebate_range(n, l1,l2,l3,l4,l5, r1,r2,r3,r4,r5, p1,p2,p3,p4,p5):
	return l1,l2,l3,l4,l5, r1,r2,r3,r4,r5, p1,p2,p3,p4,p5



# overall likelihood
@app.callback(
	Output('overall-like-user', 'children'),
	[Input('computed-table', 'data'),
	Input('target-patient-input', 'value')]
	)
def overall_like(data, cohort_selected):
	if cohort_selected == 'CHF+AF':
		df = df_setup1
	else:
		df = df_setup2
			
	dff = df if data is None else pd.DataFrame(data)
	measure_list = list(dff['measures'])
	ul_list = []
	for i in range(len(measure_list)):
		if measure_list[i] not in ['Cost & Utilization Reduction','Improving Disease Outcome','Increasing Patient Safety','Enhancing Care Quality','Better Patient Experience']:
			
			if dff['probuser'][i] == 'High':
				ul = 3 * int(dff['weight_user'][i].replace('%',''))/100
			elif dff['probuser'][i] == 'Mid':
				ul = 2 * int(dff['weight_user'][i].replace('%',''))/100
			else:
				ul = 1 * int(dff['weight_user'][i].replace('%',''))/100
			ul_list.append(ul)
	
	avg_ul = np.sum(ul_list)

	if avg_ul <= 1.5:
		user_like= 'Low'
	elif avg_ul <= 2.5:
		user_like= 'Mid'
	elif avg_ul > 2.5:
		user_like= 'High'
	else:
		user_like= ''

	return user_like


#input modal measure
@app.callback(
	Output("optimizer-modal-centered", "is_open"),
	[Input("optimizer-open-centered", "n_clicks"), Input("optimizer-close-centered", "n_clicks")],
	[State("optimizer-modal-centered", "is_open")],
	)
def toggle_modal_simulation_measure_selection(n1, n2, is_open):
	if n1 or n2:
		return not is_open
	return is_open


def toggle_collapse_domain_selection_measures(n, is_open):
	if n and n%2 == 1:
		return not is_open, "Confirm"
	elif n and n%2 == 0:
		return not is_open, "Edit"
	return is_open, "Edit"

for i in range(domain_ct):
	app.callback(
		[Output(f"optimizer-collapse-{i+1}", "is_open"), 
		 Output(f"optimizer-collapse-button-{i+1}","children")],
		[Input(f"optimizer-collapse-button-{i+1}", "n_clicks")],
		[State(f"optimizer-collapse-{i+1}", "is_open")],
	)(toggle_collapse_domain_selection_measures)


def open_measure_lv2(n, is_open):
	if n:
		return [not is_open]
	return [is_open]

for d in range(len(list(Domain_options.keys()))):
	for i in range(len(list(Domain_options[list(Domain_options.keys())[d]].keys()))):
		app.callback(
			[Output(f"optimizer-checklist-domain-measures-lv2-container-{d+1}-{i+1}","is_open")],
			[Input(f"optimizer-measures-lv1-{d+1}-{i+1}","n_clicks")],
			[State(f"optimizer-checklist-domain-measures-lv2-container-{d+1}-{i+1}","is_open")],
		)(open_measure_lv2)


def sum_selected_measure(v):
	if v and len(v) > 0:
		return "primary", u"{}".format(len(v))
	return "light", ""

for d in range(len(list(Domain_options.keys()))):
	for i in range(len(list(Domain_options[list(Domain_options.keys())[d]].keys()))):
		app.callback(
			[Output(f"optimizer-card-selected-{d+1}-{i+1}", "color"),
			Output(f"optimizer-card-selected-{d+1}-{i+1}", "children")],
			[Input(f"optimizer-checklist-domain-measures-lv2-{d+1}-{i+1}", "value")],
		)(sum_selected_measure)

## Domain 1
@app.callback(
	[Output("optimizer-collapse-card-domain-selection-1", "color"),
	Output("optimizer-collapse-card-domain-selection-1", "outline"),
	Output("optimizer-card-selected-domain-1", "children")],
	[Input("optimizer-checklist-domain-measures-lv2-1-1", "value"),
	Input("optimizer-checklist-domain-measures-lv2-1-2", "value"),
	Input("optimizer-checklist-domain-measures-lv2-1-3", "value"),
	Input("optimizer-checklist-domain-measures-lv2-1-4", "value")],
)
def toggle_collapse_domain_selection_measures_1(v1, v2, v3, v4):
	if v1:
		len1 = len(v1)
	else:
		len1 = 0
	if v2:
		len2 = len(v2)
	else:
		len2 = 0
	if v3:
		len3 = len(v3)
	else:
		len3= 0
	if v4:
		len4 = len(v4)
	else:
		len4= 0
	measure_count = len1 + len2 + len3 + len4
	if measure_count > 0: 
		return  "primary", True, u"{} measures selected".format(measure_count)
	return "light", False, ""    

## Domain 2
@app.callback(
	[Output("optimizer-collapse-card-domain-selection-2", "color"),
	Output("optimizer-collapse-card-domain-selection-2", "outline"),
	Output("optimizer-card-selected-domain-2", "children")],
	[Input("optimizer-checklist-domain-measures-lv2-2-1", "value"),
	Input("optimizer-checklist-domain-measures-lv2-2-2", "value"),
	Input("optimizer-checklist-domain-measures-lv2-2-3", "value"),
	Input("optimizer-checklist-domain-measures-lv2-2-4", "value"),
	Input("optimizer-checklist-domain-measures-lv2-2-5", "value"),
	Input("optimizer-checklist-domain-measures-lv2-2-6", "value")],
)
def toggle_collapse_domain_selection_measures_2(v1, v2, v3, v4, v5, v6):
	if v1:
		len1 = len(v1)
	else:
		len1 = 0
	if v2:
		len2 = len(v2)
	else:
		len2 = 0
	if v3:
		len3 = len(v3)
	else:
		len3= 0
	if v4:
		len4 = len(v4)
	else:
		len4= 0
	if v5:
		len5 = len(v5)
	else:
		len5= 0
	if v6:
		len6 = len(v6)
	else:
		len6= 0
	measure_count = len1 + len2 +len3 + len4 + len5 + len6
	if measure_count > 0: 
		return  "primary", True, u"{} measures selected".format(measure_count)
	return "light", False, "" 

## Domain 4
@app.callback(
	[Output("optimizer-collapse-card-domain-selection-4", "color"),
	Output("optimizer-collapse-card-domain-selection-4", "outline"),
	Output("optimizer-card-selected-domain-4", "children")],
	[Input("optimizer-checklist-domain-measures-lv2-4-1", "value")],
)
def toggle_collapse_domain_selection_measures_4(v1):
	if v1:
		measure_count = len(v1)
	else: 
		measure_count = 0
	if measure_count > 0: 
		return  "primary", True, u"{} measures selected".format(measure_count)
	return "light", False, "" 

## Domain 5
@app.callback(
	[Output("optimizer-collapse-card-domain-selection-5", "color"),
	Output("optimizer-collapse-card-domain-selection-5", "outline"),
	Output("optimizer-card-selected-domain-5", "children")],
	[Input("optimizer-checklist-domain-measures-lv2-5-1", "value")],
)
def toggle_collapse_domain_selection_measures_5(v1):
	if v1:
		measure_count = len(v1)
	else: 
		measure_count = 0
	if measure_count > 0: 
		return  "primary", True, u"{} measures selected".format(measure_count)
	return "light", False, "" 

## Domain 6
@app.callback(
	[Output("optimizer-collapse-card-domain-selection-6", "color"),
	Output("optimizer-collapse-card-domain-selection-6", "outline"),
	Output("optimizer-card-selected-domain-6", "children")],
	[Input("optimizer-checklist-domain-measures-lv2-6-1", "value")],
)
def toggle_collapse_domain_selection_measures_6(v1):
	if v1:
		measure_count = len(v1)
	else: 
		measure_count = 0
	if measure_count > 0: 
		return  "primary", True, u"{} measures selected".format(measure_count)
	return "light", False, ""   



# results
@app.callback(
	Output("optimizer-collapse_result_1", "is_open"),
	[Input("optimizer-collapse_button_result_1", "n_clicks")],
	[State("optimizer-collapse_result_1", "is_open")],
)
def toggle_collapse(n, is_open):
	if n:
		return not is_open
	return is_open


@app.callback(
	Output("optimizer-collapse_result_2", "is_open"),
	[Input("optimizer-collapse_button_result_2", "n_clicks")],
	[State("optimizer-collapse_result_2", "is_open")],
)
def toggle_collapse(n, is_open):
	if n:
		return not is_open
	return is_open


@app.callback(
	Output("optimizer-collapse_result_3", "is_open"),
	[Input("optimizer-collapse_button_result_3", "n_clicks")],
	[State("optimizer-collapse_result_3", "is_open")],
)
def toggle_collapse(n, is_open):
	if n:
		return not is_open
	return is_open


@app.callback(
	Output("optimizer-collapse_confounding_factors", "is_open"),
	[Input("optimizer-collapse_button_confounding_factors", "n_clicks")],
	[State("optimizer-collapse_confounding_factors", "is_open")],
)
def toggle_collapse(n, is_open):
	if n:
		return not is_open
	return is_open


#modal-input 
def parse_contents(contents, filename, date):
	return html.Div([
		html.H6(filename),
		html.H6(datetime.datetime.fromtimestamp(date)),
		])

def trans_upload_to_download(contents, filename, date):
	content_type, content_string = contents.split(',')
	decoded = base64.b64decode(content_string)

	filename = filename.replace(" ",'_')	
	path = str('downloads/') + filename
	with open(path, "wb") as file:
		file.write(decoded)

	return html.Div([
				html.A(filename, 
					href='http://139.224.186.182:8098/' + path,
					target = "_blank")
				])


@app.callback(
	Output('output-data-upload', 'children'),
	[Input('upload-data', 'contents')],
	[State('upload-data', 'filename'),
	State('upload-data','last_modified')]
	)
def upload_output(list_of_contents, list_of_names, list_of_dates):
	if list_of_contents is not None:
		children = [
			trans_upload_to_download(list_of_contents, list_of_names, list_of_dates) 
		]
		return children

@app.callback(
	Output('output-age-upload', 'children'),
	[Input('upload-age', 'contents')],
	[State('upload-age', 'filename'),
	State('upload-age','last_modified')]
	)
def upload_output(list_of_contents, list_of_names, list_of_dates):
	if list_of_contents is not None:
		children = [
			trans_upload_to_download(list_of_contents, list_of_names, list_of_dates)
		]
		return children

@app.callback(
	Output('output-geo-upload', 'children'),
	[Input('upload-geo', 'contents')],
	[State('upload-geo', 'filename'),
	State('upload-geo','last_modified')]
	)
def upload_output(list_of_contents, list_of_names, list_of_dates):
	if list_of_contents is not None:
		children = [
			trans_upload_to_download(list_of_contents, list_of_names, list_of_dates)
		]
		return children

@app.callback(
	Output('output-price-upload', 'children'),
	[Input('upload-price', 'contents')],
	[State('upload-price', 'filename'),
	State('upload-price','last_modified')]
	)
def upload_output(list_of_contents, list_of_names, list_of_dates):
	if list_of_contents is not None:
		children = [
			trans_upload_to_download(list_of_contents, list_of_names, list_of_dates)
		]
		return children

@app.callback(
	Output('output-rebate-upload', 'children'),
	[Input('upload-rebate', 'contents')],
	[State('upload-rebate', 'filename'),
	State('upload-rebate','last_modified')]
	)
def upload_output(list_of_contents, list_of_names, list_of_dates):
	if list_of_contents is not None:
		children = [
			trans_upload_to_download(list_of_contents, list_of_names, list_of_dates)
		]
		return children


@app.callback(
	[Output('collapse-age', 'is_open'),Output('button-collapse-age','children')],
	[Input('button-collapse-age', 'n_clicks')]
	)
def toggle_collapse(n):
	if n and n%2 == 1:
		return True, '\u25B2'
	return False, '\u25BC'

@app.callback(
	[Output('collapse-gender', 'is_open'),Output('button-collapse-gender','children')],
	[Input('button-collapse-gender', 'n_clicks')]
	)
def toggle_collapse(n):
	if n and n%2 == 1:
		return True, '\u25B2'
	return False, '\u25BC'

@app.callback(
	[Output('collapse-benefit', 'is_open'),Output('button-collapse-benefit','children')],
	[Input('button-collapse-benefit', 'n_clicks')]
	)
def toggle_collapse(n):
	if n and n%2 == 1:
		return True, '\u25B2'
	return False, '\u25BC'

@app.callback(
	[Output('collapse-month', 'is_open'),Output('button-collapse-month','children')],
	[Input('button-collapse-month', 'n_clicks')]
	)
def toggle_collapse(n):
	if n and n%2 == 1:
		return True, '\u25B2'
	return False, '\u25BC'

@app.callback(
	Output('modal-edit-assumption', 'is_open'),
	[Input('button-edit-assumption', 'n_clicks'), Input('close-edit-assumption', 'n_clicks')],
	[State('modal-edit-assumption', 'is_open')],
	)
def toggle_popover(n1, n2, is_open):
	if n1 or n2:
		return not is_open
	return is_open

@app.callback(
	Output('modal-edit-rebate-1', 'is_open'),
	[Input('button-edit-rebate-1', 'n_clicks'), Input('close-edit-rebate-1', 'n_clicks')],
	[State('modal-edit-rebate-1', 'is_open')],
	)
def toggle_popover(n1, n2, is_open):
	if n1 or n2:
		return not is_open
	return is_open

@app.callback(
	Output('modal-edit-rebate-2', 'is_open'),
	[Input('button-edit-rebate-2', 'n_clicks'), Input('close-edit-rebate-2', 'n_clicks')],
	[State('modal-edit-rebate-2', 'is_open')],
	)
def toggle_popover(n1, n2, is_open):
	if n1 or n2:
		return not is_open
	return is_open  

@app.callback(
	Output('table_setup', 'children'),
#    Output('table_setup', 'hidden'),
#    [Output('computed-table', 'data'),
#    Output('computed-table', 'selected_row_ids')],
	[Input(f'optimizer-collapse-card-domain-selection-{d+1}', 'color') for d in range(domain_ct)]
	+ [Input(f'optimizer-checklist-domain-measures-lv2-1-{n+1}', 'value') for n in range(4)]
	+ [Input(f'optimizer-checklist-domain-measures-lv2-2-{n+1}', 'value') for n in range(4)]
	+ [Input(f'optimizer-checklist-domain-measures-lv2-4-1', 'value')]
	+ [Input(f'optimizer-checklist-domain-measures-lv2-5-1', 'value')]
	+ [Input(f'optimizer-checklist-domain-measures-lv2-6-1', 'value')]
	+[Input('target-patient-input','value')]
	#+[Input('computed-table', 'data_timestamp')],
	#[State('computed-table', 'data')]
	)
def update_table(d1,d2,d3,d4,d5,d6,mc1,mc2,mc3,mc4,mc5,mc6,mc7,mc8,mc9,mc10,mc11,cohort):#,timestamp, data
	global domain_index,domain1_index,domain2_index,domain3_index,domain4_index,domain5_index,list_forborder,df_setup_filter,measures_select,df_setup,df_setup1,df_setup2,dropdown_cohort,cohort_now

	cohort_now=cohort

	ctx = dash.callback_context


	

	if cohort == 'CHF+AF':
		df_setup_dict = {'cohort': 'CHF+AF', 'data': df_setup1.to_dict()}
	else:
		df_setup_dict = {'cohort': 'All CHF Patients', 'data': df_setup2.to_dict()}

	domain_selected = []
	measure_selected = []

	d1_meas=[]
	d2_meas=[]

	for i in range(11):
		if eval('mc'+str(i+1)) and len(eval('mc'+str(i+1))) > 0:
			if i in [0,1,2,3]:
				domain_selected.append(domain_set[0])
				d1_meas.extend(eval('mc'+str(i+1)))
			elif i in [4,5,6,7]:
				domain_selected.append(domain_set[1])
				d2_meas.extend(eval('mc'+str(i+1)))
			elif i == 8:
				domain_selected.append(domain_set[3])
			elif i == 9:
				domain_selected.append(domain_set[4])
			else:
				domain_selected.append(domain_set[5])
			measure_selected.extend(eval('mc'+str(i+1)))

	measures_select = domain_selected + measure_selected



	df_setup = pd.DataFrame(df_setup_dict['data'])
	rows=df_setup[df_setup['measures'].isin(measures_select)]['id'].to_list()
	temp=df_setup[df_setup['measures'].isin(measures_select)]
	ct=0
	if domain_set[0] in domain_selected:
		ct=1+len(d1_meas)
		temp.iloc[[0],[6]]=str(temp[temp['measures'].isin(d1_meas)]['weight_recom'].apply(lambda x : int(str(x).replace('%',''))).sum())+'%'
		temp.iloc[[0],[7]]=str(temp[temp['measures'].isin(d1_meas)]['weight_user'].apply(lambda x : int(str(x).replace('%',''))).sum())+'%'

	if domain_set[1] in domain_selected:
		temp.iloc[[ct],[6]]=str(temp[temp['measures'].isin(d2_meas)]['weight_recom'].apply(lambda x : int(str(x).replace('%',''))).sum())+'%'
		temp.iloc[[ct],[7]]=str(temp[temp['measures'].isin(d2_meas)]['weight_user'].apply(lambda x : int(str(x).replace('%',''))).sum())+'%'

	domain_index=[]
	domain1_index=[]
	domain2_index=[]
	domain3_index=[]
	domain4_index=[]
	domain5_index=[]
	list_forborder=[]
	#df_setup_filter=df
	
	for i in range(len(temp)):
		list_forborder.append([i,True])
		list_forborder.append([i,False])
		if temp.values[i,0] in ['Cost & Utilization Reduction','Improving Disease Outcome','Increasing Patient Safety','Enhancing Care Quality','Better Patient Experience']:
			domain_index.append(i)
			
	for i in range(len(domain_index)):
		for j in range(len(temp)):
			if i==len(domain_index)-1:
				if(j>domain_index[i]):
					eval('domain'+str(i+1)+'_index').append(j)
			else: 
				if (j>domain_index[i]) & (j<domain_index[i+1]):
					eval('domain'+str(i+1)+'_index').append(j)

	temp_dict = {'cohort': df_setup_dict['cohort'], 'data': temp.to_dict()}             
	return table_setup(temp_dict,cohort) 
	



@app.callback(
	Output('computed-table', 'data'),
	[Input('computed-table', 'data_timestamp')],
	[State('computed-table', 'data')])
def update_columns(timestamp, data):


	global measures_select,df_setup_filter

	weight_1=0
	weight_2=0
	weight_3=0
	weight_4=0
	weight_5=0

	weight_1_recom=0
	weight_2_recom=0
	weight_3_recom=0
	weight_4_recom=0
	weight_5_recom=0

	for i in domain1_index+domain2_index+domain3_index+domain4_index+domain5_index:

		row=data[i]
		row['weight_user']=str(row['weight_user']).replace('$','').replace('%','').replace(',','')
		row['taruser_value']=str(row['taruser_value']).replace('$','').replace('%','').replace(',','')

		if i in domain1_index:
			weight_1=weight_1+int(row['weight_user'])
		if i in domain2_index:
			weight_2=weight_2+int(row['weight_user'])
		if i in domain3_index:
			weight_3=weight_3+int(row['weight_user'])
		if i in domain4_index:
			weight_4=weight_4+int(row['weight_user'])
		if i in domain5_index:
			weight_5=weight_5+int(row['weight_user'])
			
		row['weight_user']= '{}%'.format(row['weight_user']) 
		
		
		if row['measures'] in ["LVEF LS Mean Change %", "Change in Self-Care Score", "Change in Mobility Score", "DOT", "PDC", "MPR"] :

			if float(row['taruser_value'])<=float(row['yellow_thres']):
				row['highlight_user']='yellow'
				row['probuser']='Mid'
				if float(row['taruser_value'])<=float(row['green_thres']):
					row['highlight_user']='green'
					row['probuser']='High'
			else:
				row['highlight_user']='red'
				row['probuser']='Low'
				
		else:

			if float(row['taruser_value'])>=float(row['yellow_thres']):
				row['highlight_user']='yellow'
				row['probuser']='Mid'
				if float(row['taruser_value'])>=float(row['green_thres']):
					row['highlight_user']='green'
					row['probuser']='High'
			else:
				row['highlight_user']='red'
				row['probuser']='Low'
	   
		if row['measures'] not in ['CHF Related Average Cost per Patient','CHF Related Average IP Cost per Patient','All Causes Average Cost per Patient','All Causes Average IP Cost per Patient']:
			if row['measures'] != 'CHF Related Hospitalization Rate':
				row['taruser_value']='{}%'.format(row['taruser_value'])
		else:
			row['taruser_value']='${:,}'.format(int(row['taruser_value'])) 
	
	j=0
	for i in domain_index:
		j=j+1
		data[i]['taruser_value']=''
		data[i]['weight_user']=str(eval('weight_'+str(j)))+'%'


	df_setup_filter=pd.DataFrame(data)

	return data 

@app.callback(
	Output('temp-data','children'),
	[Input('close-edit-realtime-assumption', 'n_clicks')],
	[State('realtime-assump-input-trend','value'),
	State('realtime-assump-input-iprate', 'value'),
	State('realtime-assump-input-hospitalization', 'value'),
	State('realtime-assump-input-probnp', 'value'),
	State('realtime-assump-input-lvef', 'value'),
	State('realtime-assump-input-utilizer', 'value'),
	State('realtime-assump-input-script', 'value'),
	State('realtime-assump-input-rebatevbc', 'value')]
	+[State(f'vbc-l-{i+1}-input', 'value') for i in range(5)]
	+[State(f'vbc-r-{i+1}-input', 'value') for i in range(5)]
	+[State(f'vbc-p-{i+1}-input', 'value') for i in range(5)]
	+[State(f'realtime-assump-month-{i+1}', 'value') for i in range(12)]
	)
def data_prep(save_assump, cost_trend,util_trend,hr_input,probnp_input,lvef_input,Entresto_Utilizer_Perc,Script_PMPM,rebate_vbc, l1,l2,l3,l4,l5,r1,r2,r3,r4,r5,p1,p2,p3,p4,p5,m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,m11,m12):
	
	global df_setup1,df_setup2,df_setup_filter,dropdown_cohort
	if save_assump:
		if l1 is None:
			input5 = {'Marketshare_L':[],
				 'Marketshare_H':[],
				 'Rebate':[]}
		else:
			vbc_l = list(filter(None,[l1+1, l2, l3, l4, l5]))
			vbc_r = list(filter(None,[r1, r2, r3, r4, r5]))
			vbc_p = list(filter(None,[p1, p2, p3, p4, p5]))
			input5 = {'Marketshare_L':[vbc_l[i]-1 if i==0 else vbc_l[i] for i in range(len(vbc_l))],
					 'Marketshare_H':vbc_r,
					 'Rebate':vbc_p}
		Rebate_VBC_table=pd.DataFrame(input5, columns = ['Marketshare_L', 'Marketshare_H', 'Rebate'])
		Rebate_VBC_table['Marketshare_L'] = Rebate_VBC_table['Marketshare_L'].apply(int)/100
		Rebate_VBC_table['Marketshare_H'] = Rebate_VBC_table['Marketshare_H'].apply(int)/100
		Rebate_VBC_table['Rebate'] = Rebate_VBC_table['Rebate'].apply(int)/100

		if rebate_vbc is None:
			rebate_vbc_flat = 0
		else:
			rebate_vbc_flat = rebate_vbc/100

		input6={'Month':[1,2,3,4,5,6,7,8,9,10,11,12],
			'MarketShare':[m1/100,m2/100,m3/100,m4/100,m5/100,m6/100,m7/100,m8/100,m9/100,m10/100,m11/100,m12/100]}
		MarketShare_table=pd.DataFrame(input6, columns = ['Month','MarketShare'])


		t1, t2, t3, t4, t5 ,t6, t7= simulate_input(cost_trend/100,util_trend/100,hr_input/100,-probnp_input/100,lvef_input/100,Entresto_Utilizer_Perc/100,Script_PMPM,rebate_vbc_flat,Rebate_VBC_table,MarketShare_table)       

		df_setup1=t7
		df_setup2=t6

		t1.to_csv('df_perfom_assump.csv')
		t2.to_csv('df_recom_measure.csv')

		if t3=='CHF+AF':
			df_setup_filter=df_setup1
		else:
			df_setup_filter=df_setup2

		dropdown_cohort=t3
	
		result = {'df_perfom_assump': t1.to_dict(), 'df_recom_measure': t2.to_dict(), 'recom_cohort':t3, 'meas_recom':t4, 'meas_recom_not':t5, 'setup_all':t6.to_dict(),  'setup_af':t7.to_dict()}
		
		with open('configure/optimizer_input.json','w') as outfile:
			json.dump(result, outfile)

		return json.dumps(result)


@app.callback(
	[Output('target-patient-input', 'options'),
	Output('target-patient-input', 'value')],
	[Input('temp-data', 'children')]
	)
def update_recom_cohort(temp):
	global dropdown_cohort
	result = json.load(open('configure/optimizer_input.json', encoding = 'utf-8'))
#	result = json.loads(temp)
	recom_cohort = result['recom_cohort']

	dropdown_cohort=recom_cohort
	
	if recom_cohort == 'CHF+AF':
		return [{'label':'CHF+AF (Recommended)', 'value':'CHF+AF'}, {'label':'All CHF Patients', 'value':'All CHF Patients'}], 'CHF+AF'
	else:
		return [{'label':'CHF+AF', 'value':'CHF+AF'}, {'label':'All CHF Patients (Recommended)', 'value':'All CHF Patients'}], 'All CHF Patients'



@app.callback(
	[Output('optimizer-checklist-domain-measures-lv2-1-1', 'value'),
	Output('optimizer-checklist-domain-measures-lv2-1-3', 'value'),
	Output('optimizer-checklist-domain-measures-lv2-2-1', 'value')],
	[Input('temp-data', 'children'),
	Input('target-patient-input', 'value')]
	)
def update_measure_selection(temp, v):
	result = json.load(open('configure/optimizer_input.json', encoding = 'utf-8'))

	meas_recom = result['meas_recom']
	meas_recom_not = result['meas_recom_not']
	recom_cohort = result['recom_cohort']

	measures_1_1 = ["All Causes Average Cost per Patient", "CHF Related Average Cost per Patient"]
	measures_1_3 = ["All Causes Hospitalization Rate", "CHF Related Hospitalization Rate"]
	measures_2_1 = ["NT-proBNP Change %", "LVEF LS Mean Change %", "LAVi LS Mean Change", "LVEDVi LS Mean Change", "LVESVi LS Mean Change", "E/e' LS Mean Change"]

	if v==recom_cohort:
		value_1_1 = list(set(measures_1_1).intersection(set(meas_recom)))
		value_1_3 = list(set(measures_1_3).intersection(set(meas_recom)))
		value_2_1 = list(set(measures_2_1).intersection(set(meas_recom)))
	else:
		value_1_1 = list(set(measures_1_1).intersection(set(meas_recom_not)))
		value_1_3 = list(set(measures_1_3).intersection(set(meas_recom_not)))
		value_2_1 = list(set(measures_2_1).intersection(set(meas_recom_not)))

	return value_1_1, value_1_3, value_2_1





@app.callback(
	[Output('tab_container', 'active_tab'),
	Output('sim_result_box_1','figure'),
	Output('sim_result_table_1','children'),
	Output('sim_result_box_2','figure'),
	Output('sim_result_table_2','children'),
	Output('sim_result_box_3','figure'),
	Output('sim_result_table_3','children')],
	[Input('button-simulation-submit', 'n_clicks')],
	[State('recom-pos-perf','children'),
	State('recom-neg-perf','children'),
	State('input-max-pos-adj','value'),
	State('input-max-neg-adj','value'),
	State('input-pos-perform', 'value'),
	State('input-neg-perform', 'value'),
#	State('input-pos-adj', 'value'),
#	State('input-neg-adj', 'value'),
	State('target-patient-recom','children'),
	State('target-patient-input','value'),
	State('input-rebate','value'),
	State('input-base-rebate','value'),]
	+[State('computed-table','derived_virtual_data')]
	+[State(f'novbc-l-{i+1}-input', 'value') for i in range(5)]
	+[State(f'novbc-r-{i+1}-input', 'value') for i in range(5)]
	+[State(f'novbc-p-{i+1}-input', 'value') for i in range(5)]
	+[State(f'vbc-l-{i+1}-input', 'value') for i in range(5)]
	+[State(f'vbc-r-{i+1}-input', 'value') for i in range(5)]
	+[State(f'vbc-p-{i+1}-input', 'value') for i in range(5)]
	+[State(f'realtime-assump-month-{i+1}', 'value') for i in range(12)]
	+[State('realtime-assump-input-utilizer', 'value'),
	State('realtime-assump-input-script', 'value'),
	State('temp-data','children')]
)
def simulation(submit_button, re_pos_perf, re_neg_perf, re_pos_adj, re_neg_adj, in_pos_perf, in_neg_perf, cohort_recom, cohort_selected, rebate_novbc, rebate_vbc, data, nl1,nl2,nl3,nl4,nl5, nr1,nr2,nr3,nr4,nr5, np1,np2,np3,np4,np5, l1,l2,l3,l4,l5, r1,r2,r3,r4,r5, p1,p2,p3,p4,p5, m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,m11,m12, utilizer, script, temp ):

	

#   cohort_selected = cohort_selected.replace(' (Recommended)','')
#   triggered = [t["prop_id"] for t in dash.callback_context.triggered]
#   submit = len([1 for i in triggered if i == "button-simulation-submit.n_clicks"])
#   if submit:
	if submit_button:
		result = json.load(open('configure/optimizer_input.json', encoding = 'utf-8'))
#		result = json.loads(temp)
		Performance_assumption = pd.DataFrame(result['df_perfom_assump'])
		Recom_Measure_all = pd.DataFrame(result['df_recom_measure'])

		if cohort_selected == 'CHF+AF':
			df = df_setup1
		else:
			df = df_setup2
		
		dff = df if data is None else pd.DataFrame(data)
		
		input1 = {'Perf_Range_U_Min': [1], 
					'Perf_Range_U_Max': [float(re_pos_perf[:-1])/100], 
					'Adj_Limit_U': [re_pos_adj/100],
					'Perf_Range_L_Min': [1],
					'Perf_Range_L_Max': [float(re_neg_perf[:-1])/100],
					'Adj_Limit_L': [-re_neg_adj/100]} 
		Recom_Contract = pd.DataFrame(input1, columns = ['Perf_Range_U_Min','Perf_Range_U_Max','Adj_Limit_U','Perf_Range_L_Min','Perf_Range_L_Max', 'Adj_Limit_L'])
		

		measure_list = list(dff['measures'])
		measure_name = []
		target_list = []
		weight_list = []
		for i in range(len(measure_list)):
			if measure_list[i] not in ['Cost & Utilization Reduction','Improving Disease Outcome','Increasing Patient Safety','Enhancing Care Quality','Better Patient Experience']:
				measure_name.append(measure_list[i])
				target_list.append(float(str(list(dff['taruser_value'])[i]).replace('$','').replace('%','').replace(',','')))
				weight_list.append(float(str(list(dff['weight_user'])[i]).replace('$','').replace('%','').replace(',','')))  
				

		input2 = {'Measure': measure_name, 
				'Target': target_list, 
				'Weight': list(np.array(weight_list)/100)} 
		UD_Measure = pd.DataFrame(input2, columns = ['Measure', 'Target', 'Weight']) 
		UD_Measure['Target'] = UD_Measure.apply(lambda x: x['Target']/100 if x['Measure'] in percent_input else x['Target'], axis = 1)

		input3 = {'Perf_Range_U_Min': [1], 
						'Perf_Range_U_Max': [in_pos_perf/100], 
						'Adj_Limit_U': [re_pos_adj/100],
						'Perf_Range_L_Min': [1],
						'Perf_Range_L_Max': [in_neg_perf/100],
						'Adj_Limit_L': [-re_neg_adj/100]} 
		UD_Contract = pd.DataFrame(input3, columns = ['Perf_Range_U_Min','Perf_Range_U_Max','Adj_Limit_U','Perf_Range_L_Min','Perf_Range_L_Max', 'Adj_Limit_L']) 

		if nl1 is None:
			input4 = {'Marketshare_L':[],
				 'Marketshare_H':[],
				 'Rebate':[]}
		else:
			novbc_l = list(filter(None,[nl1+1, nl2, nl3, nl4, nl5]))
			novbc_r = list(filter(None,[nr1, nr2, nr3, nr4, nr5]))
			novbc_p = list(filter(None,[np1, np2, np3, np4, np5]))
			input4 = {'Marketshare_L':[novbc_l[i]-1 if i==0 else novbc_l[i] for i in range(len(novbc_l))],
					 'Marketshare_H':novbc_r,
					 'Rebate':novbc_p}
		Rebate_noVBC_table=pd.DataFrame(input4, columns = ['Marketshare_L', 'Marketshare_H', 'Rebate'])
		Rebate_noVBC_table['Marketshare_L'] = Rebate_noVBC_table['Marketshare_L'].apply(int)/100
		Rebate_noVBC_table['Marketshare_H'] = Rebate_noVBC_table['Marketshare_H'].apply(int)/100
		Rebate_noVBC_table['Rebate'] = Rebate_noVBC_table['Rebate'].apply(int)/100
		
		if l1 is None:
			input5 = {'Marketshare_L':[],
				 'Marketshare_H':[],
				 'Rebate':[]}
		else:
			vbc_l = list(filter(None,[l1+1, l2, l3, l4, l5]))
			vbc_r = list(filter(None,[r1, r2, r3, r4, r5]))
			vbc_p = list(filter(None,[p1, p2, p3, p4, p5]))
			input5 = {'Marketshare_L':[vbc_l[i]-1 if i==0 else vbc_l[i] for i in range(len(vbc_l))],
					 'Marketshare_H':vbc_r,
					 'Rebate':vbc_p}
		Rebate_VBC_table=pd.DataFrame(input5, columns = ['Marketshare_L', 'Marketshare_H', 'Rebate'])
		Rebate_VBC_table['Marketshare_L'] = Rebate_VBC_table['Marketshare_L'].apply(int)/100
		Rebate_VBC_table['Marketshare_H'] = Rebate_VBC_table['Marketshare_H'].apply(int)/100
		Rebate_VBC_table['Rebate'] = Rebate_VBC_table['Rebate'].apply(int)/100

		input6={'Month':[1,2,3,4,5,6,7,8,9,10,11,12],
			'MarketShare':[m1/100,m2/100,m3/100,m4/100,m5/100,m6/100,m7/100,m8/100,m9/100,m10/100,m11/100,m12/100]}

		MarketShare_table=pd.DataFrame(input6, columns = ['Month','MarketShare'])


		if rebate_novbc is None:
			rebate_novbc_flat = 0
		else:
			rebate_novbc_flat = rebate_novbc/100

		if rebate_vbc is None:
			rebate_vbc_flat = 0
		else:
			rebate_vbc_flat = rebate_vbc/100
		
		Recom_Contract.to_csv('Recom_Contract.csv')
		UD_Measure.to_csv('UD_Measure.csv')
		UD_Contract.to_csv('UD_Contract.csv')

		t1,t2,t3=Contract_Calculation(Recom_Contract, UD_Measure,UD_Contract,cohort_selected,rebate_novbc_flat, rebate_vbc_flat, Rebate_noVBC_table,Rebate_VBC_table, MarketShare_table, utilizer/100, script, Performance_assumption, Recom_Measure_all)
		t1.reset_index(inplace = True)
		t2.reset_index(inplace = True)
		t3.reset_index(inplace  =True)



		return 'tab-1',sim_result_box(t1),table_sim_result(t1),sim_result_box(t2),table_sim_result(t2),sim_result_box(t3),table_sim_result(t3)
	return 'tab-0',{},[],{},[],{},[]




if __name__ == "__main__":
	app.run_server(host="127.0.0.1",debug=True, port = 8052)

