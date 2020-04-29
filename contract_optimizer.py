#!/usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import datetime
import pandas as pd
import numpy as np

import pathlib
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State

from utils import *
from figure import *

from modal_simulation_measure_selection import *
from contract_calculation import *
from modal_simulation_input import *

from app import app

df_sim_rev=pd.read_csv("data/Output_Pharma_Net_Revenue.csv")
df_sim_rebate=pd.read_csv("data/Output_Rebate.csv")
df_sim_cost=pd.read_csv("data/Total_Cost.csv")

## setup
#df_setup=pd.read_csv("data/setup.csv")
df_setup1=pd.read_csv("data/setup_1.csv")
df_setup2=pd.read_csv("data/setup_2.csv")
df_initial=df_setup1[df_setup1['id'].isin([0,1,2,9,11])]
## 初始化
global measures_select,df_setup_filter

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
                    
                    html.Div(
                        [
                            dbc.Tabs(
							    [
							        dbc.Tab(tab_setup(app), label="Contract Simulation Setup", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
							        dbc.Tab(tab_result(app), label="Result", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
							        
							    ], id = 'tab_container'
							)
                        ],
                        className="mb-3",
                        style={"padding-left":"3rem", "padding-right":"3rem"},
                    ),
                    
                ],
                style={"background-color":"#f5f5f5"},
            )

def table_setup(df,cohort_change):#,rows
    global df_setup_filter,domain_index,domain1_index,domain2_index,domain3_index,domain4_index,domain5_index

    if cohort_change:
        dff=df
        
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
                
    )
    return table 

def tab_setup(app):
	return html.Div(
				[
					dbc.Row(
						[
							dbc.Col(html.H1("Contract Simulation Setup", style={"padding-left":"2rem","font-size":"3"}), width=9),
							dbc.Col([
                                modal_simulation_input()
                                ], 
                                width=3,
                                style={"padding-top":"1rem"}),
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
                        dbc.Button("Submit for Simulation", color="primary",id = 'button-simulation-submit', style={"border-radius":"10rem","box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)"})
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
                                                options = [{'label':'CHF+AF (Recommended)', 'value':'CHF+AF (Recommended)'},
                                                            {'label':'All CHF Patients', 'value':'All CHF Patients'}],
                                                value = 'CHF+AF (Recommended)',
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
                                            "Value based measures are recommended based on each measure’s stability, improvement level from baseline, data availability and ease to implement/monitor, efficacy results from clinical trials, payer’s acceptance level, pharma’s preference, etc.",
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
#                                	dbc.Button("Edit Assumption"),
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
                                                            "Recommended target is determined as the threshold value where the probability to achieve is no less than a predetermined threshold (can be customized)",
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
                                				html.H4("Likelihood to achieve", style={"font-size":"1rem"}),
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
                        html.Div([table_setup(df_initial,False)],id='table_setup'),
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
                                dbc.Col(html.Div(id = 'overall-like-recom'), width=1),
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
                                                                type = 'number', debounce = True, persistence = True, persistence_type = 'session',
                                                                min = 0, max = 100, size="13", style={"text-align":"center"}), 
                                                    dbc.InputGroupAddon("%", addon_type="append"),
                                                ],
                                                className="mb-3",
                                                size="sm"
                                            ),
                                    width=2
                                ),
								dbc.Col([
									dbc.Button("Edit Rebate Input", id = 'button-edit-rebate-1', style={"background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Regular", "font-size":"0.6rem"}),
									dbc.Modal([
										dbc.ModalHeader(html.H1("EDIT Rebate Input", style={"font-size":"1rem"})),
										dbc.ModalBody([
											dbc.Row([
												dbc.Col("% of market share range"),
												dbc.Col("Rebates %"),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(dbc.InputGroup([
													dbc.Input(),
													dbc.InputGroupAddon('~', addon_type = 'append'),
													dbc.Input(),
													])),
												dbc.Col(dbc.InputGroup([
													dbc.Input(),
													dbc.InputGroupAddon('%', addon_type = 'append'),
													])),
												],
												style={"padding":"1rem"}),
											dbc.Row([
												dbc.Col(html.H4("+ Add another range", style={"font-size":"0.8rem","color":"#1357DD"}), ),
												],
												style={"padding":"1rem"}),
											]),
										dbc.ModalFooter(
											dbc.Button('SAVE', id = 'close-edit-rebate-1', size="sm")
											)
										], id = 'modal-edit-rebate-1'),
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
                                                        type = 'number', debounce = True, persistence = True, persistence_type = 'session',
                                                        min = 0, max = 100, size="13",style={"text-align":"center"}), 
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
                                    dbc.Button("EDIT Rebate Input", id = 'button-edit-rebate-2', style={"background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Regular", "font-size":"0.6rem"}),
                                    dbc.Modal([
                                        dbc.ModalHeader(html.H1("Edit Rebate Input", style={"font-size":"1rem"})),
                                        dbc.ModalBody([
                                            dbc.Row([
                                                dbc.Col("% of market share range"),
                                                dbc.Col("Rebates %"),
                                                ],
                                                style={"padding":"1rem"}),
                                            dbc.Row([
                                                dbc.Col(dbc.InputGroup([
                                                    dbc.Input(),
                                                    dbc.InputGroupAddon('~', addon_type = 'append'),
                                                    dbc.Input(),
                                                    ])),
                                                dbc.Col(dbc.InputGroup([
                                                    dbc.Input(),
                                                    dbc.InputGroupAddon('%', addon_type = 'append'),
                                                    ])),
                                                ],
                                                style={"padding":"1rem"}),
                                            dbc.Row([
                                                dbc.Col(html.H4("+ Add another range", style={"font-size":"0.8rem","color":"#1357DD"})),
                                                ],
                                                style={"padding":"1rem"}),
                                            ]),
                                        dbc.ModalFooter(
                                            dbc.Button('SAVE', id = 'close-edit-rebate-2', size="sm")
                                            )
                                        ], id = 'modal-edit-rebate-2'),
                                    ], width=2
                                ),

                                dbc.Col(
                                    html.Div(
                                        [
                                            html.Div("VBC Adjustment Method", style={"font-family":"NotoSans-Condensed","font-size":"1rem","text-align":"start"}),
                                            dcc.Dropdown(
                                                options = [
                                                                {'label':'Rebate adjustment', 'value':'Rebate adjustment'},
                                                                {'label':'Shared savings/losses', 'value':'Shared savings/losses'},
                                                                {'label':'Outcome guarantee', 'value':'Outcome guarantee'}
                                                            ],
                                                value = 'Rebate adjustment',
                                                style={"font-family":"NotoSans-Regular","font-size":"0.8rem","width":"11rem"}
                                            )
                                                
                                        ]
                                    ),
                                    width=3
                                ),
                                    
#								dbc.Col(html.Div("Maximum Positive Adjustment"), width=1),


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
                                                min = 0, max = 100, size="6", style={"text-align":"center"}), 
                                            dbc.InputGroupAddon("%", addon_type="append"),
                                        ],
                                        className="mb-3",
                                        size="sm"
                                    ),
                                    width=3,
                                    style={"text-align":"end"}
                                ),
                                dbc.Col(
                                    dbc.InputGroup(
                                        [
                                            dcc.Input(id = 'input-pos-adj',
                                                type = 'number', debounce = True, persistence = True, persistence_type = 'session',
                                                min = 0, size="6",style={"text-align":"center"}), 
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
                                                min = 0, max = 100, size="4", style={"text-align":"center"}), 
                                            dbc.InputGroupAddon("%", addon_type="append"),
                                        ],
                                        className="mb-3",
                                        size="sm"
                                    ),
                                    width=3,
                                    style={"text-align":"end"}
                                ),
                                dbc.Col(
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupAddon("-", addon_type="prepend"),
                                            dcc.Input(id = 'input-neg-adj',
                                                type = 'number', debounce = True, persistence = True, persistence_type = 'session',
                                                min = 0, max = 100, size="4",style={"text-align":"center"}), 
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






'''
##input likelihood

def cal_measure_likelihood(recom_like, recom_target, user_target, measure, h):
    if h == False:
        if user_target:
            if recom_like[0] == 'High':
                rl = 3
            elif recom_like[0] == 'Mid':
                rl = 2
            else:
                rl = 1
            if measure in percent_input:
            	ur_target = user_target/100
            else: 
            	ur_target = user_target

            if measure in positive_measure:
                if (ur_target-recom_target[0])/recom_target[0] > 0.1:
                    ul = rl -2
                elif (ur_target-recom_target[0])/recom_target[0] > 0.05:
                    ul = rl -1
                elif (ur_target-recom_target[0])/recom_target[0] < -0.05:
                    ul = rl +1
                elif (ur_target-recom_target[0])/recom_target[0] < -0.1:
                    ul = rl +2
                else:
                    ul = rl
            else:
                if (ur_target-recom_target[0])/recom_target[0] > 0.1:
                    ul = rl +2
                elif (ur_target-recom_target[0])/recom_target[0] > 0.05:
                    ul = rl +1
                elif (ur_target-recom_target[0])/recom_target[0] < -0.05:
                    ul = rl -1
                elif (ur_target-recom_target[0])/recom_target[0] < -0.1:
                    ul = rl -2
                else:
                    ul = rl

            if ul <= 1:
                return ['Low',{"background-color": '#C00000'}]
            elif ul == 2:
                return ['Mid',{"background-color": '#ffffff'}]
            else:
                return ['High',{"background-color": '#ffffff'}]
        return ['',{"background-color": '#ffffff'}]
    return ['',{"background-color": '#ffffff'}]

for d in range(domain_ct):
    for m in range(domain_measure[domain_set[d]]):
        app.callback(
            [Output(f'measure-like-user-{d+1}-{m+1}', 'children'),
            Output(f'measure-like-user-{d+1}-{m+1}', 'style')],
            [Input(f'measure-like-recom-{d+1}-{m+1}', 'children'),
            Input(f'measure-target-recom-{d+1}-{m+1}', 'children'),
            Input(f'measure-target-user-{d+1}-{m+1}', 'value'),
            Input(f'measure-name-{d+1}-{m+1}', 'children'),
            Input(f'outcome-measure-row-{d+1}-{m+1}', 'hidden')]
            )(cal_measure_likelihood)
'''
# overall likelihood
@app.callback(
    [Output('overall-like-recom', 'children'),
    Output('overall-like-user', 'children'),],
    [Input('computed-table', 'data'),
    Input('target-patient-input', 'value')]
    )
def overall_like(data, cohort_selected):
    if cohort_selected == 'CHF+AF (Recommended)':
            df = df_setup1
    else:
        df = df_setup2
            
    dff = df if data is None else pd.DataFrame(data)
    measure_list = list(dff['measures'])
    ml_list = []
    ul_list = []
    for i in range(len(measure_list)):
        if measure_list[i] not in ['Cost & Utilization Reduction','Improving Disease Outcome','Increasing Patient Safety','Enhancing Care Quality','Better Patient Experience']:
            if dff['probrecom'][i] == 'High':
                ml = 3
            elif dff['probrecom'][i] == 'Mid':
                ml = 2
            else:
                ml = 1
            ml_list.append(ml)
            
            if dff['probuser'][i] == 'High':
                ul = 3
            elif dff['probuser'][i] == 'Mid':
                ul = 2
            else:
                ul = 1
            ul_list.append(ul)
    
    avg_ul = np.mean(ul_list)
    avg_ml = np.mean(ml_list)
    if avg_ml <= 1.5:
        recom_like= 'Low'
    elif avg_ml <= 2.5:
        recom_like= 'Mid'
    elif avg_ml > 2.5:
        recom_like= 'High'
    else:
        recom_like= ''

    if avg_ul <= 1.5:
        user_like= 'Low'
    elif avg_ul <= 2.5:
        user_like= 'Mid'
    elif avg_ul > 2.5:
        user_like= 'High'
    else:
        user_like= ''

    return recom_like,user_like

'''   
@app.callback(
    [Output('overall-like-user', 'children'),
    Output('overall-like-user', 'style')],
    [Input(f'measure-like-user-1-{m+1}', 'children') for m in range(8)]
    + [Input(f'measure-like-user-2-{m+1}', 'children') for m in range(10)]
    + [Input(f'measure-like-user-4-{m+1}', 'children') for m in range(2)]
    + [Input(f'measure-like-user-5-{m+1}', 'children') for m in range(3)]
    + [Input(f'measure-like-user-6-{m+1}', 'children') for m in range(4)]
    )
def overall_like(l1,l2,l3,l4,l5,l6,l7,l8,l9,l10,l11,l12,l13,l14,l15,l16,l17,l18,l19,l20,l21,l22,l23,l24,l25,l26,l27):
    ml_list = []
    for i in range(27):
        if eval('l'+str(i+1)):
            if eval('l'+str(i+1) ) == 'High':
                ml = 3
            elif eval('l'+str(i+1)) == 'Mid':
                ml = 2
            elif eval('l'+str(i+1) ) == 'Low':
                ml = 1
            ml_list.append(ml)
    if len(ml_list) > 0:
        avg_ml = np.mean(ml_list)
        if avg_ml <= 1.5:
            return 'Low', {"background-color": '#C00000'}
        elif avg_ml <= 2.5 and avg_ml > 1.5:
            return 'Mid',{"background-color": '#ffffff'}
        elif avg_ml > 2.5:
            return 'High',{"background-color": '#ffffff'}
        else:
            return '',{"background-color": '#ffffff'}
    else:
        return '',{"background-color": '#ffffff'}

'''
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
    [Output("optimizer-card-domain-selection-1", "color"),
    Output("optimizer-card-domain-selection-1", "outline"),
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
    [Output("optimizer-card-domain-selection-2", "color"),
    Output("optimizer-card-domain-selection-2", "outline"),
    Output("optimizer-card-selected-domain-2", "children")],
    [Input("optimizer-checklist-domain-measures-lv2-2-1", "value"),
    Input("optimizer-checklist-domain-measures-lv2-2-2", "value"),
    Input("optimizer-checklist-domain-measures-lv2-2-3", "value")],
)
def toggle_collapse_domain_selection_measures_2(v1, v2, v3):
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
    measure_count = len1 + len2 +len3
    if measure_count > 0: 
        return  "primary", True, u"{} measures selected".format(measure_count)
    return "light", False, "" 

## Domain 4
@app.callback(
    [Output("optimizer-card-domain-selection-4", "color"),
    Output("optimizer-card-domain-selection-4", "outline"),
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
    [Output("optimizer-card-domain-selection-5", "color"),
    Output("optimizer-card-domain-selection-5", "outline"),
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
    [Output("optimizer-card-domain-selection-6", "color"),
    Output("optimizer-card-domain-selection-6", "outline"),
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

@app.callback(
	Output('output-data-upload', 'children'),
	[Input('upload-data', 'contents')],
	[State('upload-data', 'filename'),
	State('upload-data','last_modified')]
	)
def upload_output(list_of_contents, list_of_names, list_of_dates):
	if list_of_contents is not None:
		children = [
			parse_contents(list_of_contents, list_of_names, list_of_dates) 
		]
		return children


@app.callback(
	Output('popover-age', 'is_open'),
	[Input('button-popover-age', 'n_clicks'), Input('popover-age-submit', 'n_clicks')],
	[State('popover-age', 'is_open')],
	)
def toggle_popover(n1, n2, is_open):
	if n1 or n2:
		return not is_open
	return is_open

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
    global domain_index,domain1_index,domain2_index,domain3_index,domain4_index,domain5_index,list_forborder,df_setup_filter,measures_select,df_setup
   
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'target-patient-input.value':
        cohort_change = True
    else:
        cohort_change = False
    if cohort == 'CHF+AF (Recommended)':
        df_setup = df_setup1
    else:
        df_setup = df_setup2

    domain_selected = []
    measure_selected = []
    for i in range(11):
        if eval('mc'+str(i+1)) and len(eval('mc'+str(i+1))) > 0:
            if i in [0,1,2,3]:
                domain_selected.append(domain_set[0])
            elif i in [4,5,6,7]:
                domain_selected.append(domain_set[1])
            elif i == 8:
                domain_selected.append(domain_set[3])
            elif i == 9:
                domain_selected.append(domain_set[4])
            else:
                domain_selected.append(domain_set[5])
            measure_selected.extend(eval('mc'+str(i+1)))

    measures_select = domain_selected + measure_selected
    #print(measures_select)
    #df=df_setup[df_setup['measures'].isin(measures_select)]
    rows=df_setup[df_setup['measures'].isin(measures_select)]['id'].to_list()
    temp=df_setup[df_setup['measures'].isin(measures_select)]
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
                    
    return table_setup(temp,cohort_change) 
    

#    return False #table_setup(df)

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
    [Output('tab_container', 'active_tab'),
    Output('sim_result_box_1','figure'),
    Output('sim_result_table_1','children'),
    Output('sim_result_box_2','figure'),
    Output('sim_result_table_2','children'),
    Output('sim_result_box_3','figure'),
    Output('sim_result_table_3','children')],
    [Input('button-simulation-submit', 'n_clicks'),
    Input('recom-pos-perf','children'),
    Input('recom-neg-perf','children'),
    Input('input-max-pos-adj','value'),
    Input('input-max-neg-adj','value'),
    Input('input-pos-perform', 'value'),
    Input('input-neg-perform', 'value'),
    Input('input-pos-adj', 'value'),
    Input('input-neg-adj', 'value'),
    Input('target-patient-recom','children'),
    Input('target-patient-input','value'),
    Input('input-rebate','value'),
    Input('input-base-rebate','value'),]
    +[Input('computed-table','derived_virtual_data')]
)
def simulation(submit_button, re_pos_perf, re_neg_perf, re_pos_adj, re_neg_adj, in_pos_perf, in_neg_perf, in_pos_adj, in_neg_adj, cohort_recom, cohort_selected, rebate_novbc, rebate_vbc,data):

    if cohort_selected == 'CHF+AF (Recommended)':
        df = df_setup1
    else:
        df = df_setup2
    triggered = [t["prop_id"] for t in dash.callback_context.triggered]
    submit = len([1 for i in triggered if i == "button-simulation-submit.n_clicks"])
    if submit:
        
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
                        'Adj_Limit_U': [in_pos_adj/100],
                        'Perf_Range_L_Min': [1],
                        'Perf_Range_L_Max': [in_neg_perf/100],
                        'Adj_Limit_L': [-in_neg_adj/100]} 
        UD_Contract = pd.DataFrame(input3, columns = ['Perf_Range_U_Min','Perf_Range_U_Max','Adj_Limit_U','Perf_Range_L_Min','Perf_Range_L_Max', 'Adj_Limit_L']) 

        t1,t2,t3=Contract_Calculation(Recom_Contract, UD_Measure,UD_Contract,cohort_selected,rebate_novbc/100, rebate_vbc/100)
        t1.reset_index(inplace = True)
        t2.reset_index(inplace = True)
        t3.reset_index(inplace  =True)

        return 'tab-1',sim_result_box(t1),table_sim_result(t1),sim_result_box(t2),table_sim_result(t2),sim_result_box(t3),table_sim_result(t3)
    return 'tab-0',{},[],{},[],{},[]

if __name__ == "__main__":
    app.run_server(host="127.0.0.1",debug=True)

