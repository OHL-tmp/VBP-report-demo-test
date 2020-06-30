#!/usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import pandas as pd
import numpy as np

import pathlib
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State

from utils import *
from figure import *

from modal_drilldown_tableview_kccq import *

from app import app


df_drill_barchart_kccq=pd.read_csv("data/drilldown barchart kccq.csv")
df_drill_piechart_kccq=pd.read_csv("data/drilldown piechart kccq.csv")

df_driver_kccq=pd.read_csv("data/Drilldown Odometer kccq.csv")

df_drilldown=pd.read_csv("data/drilldown_sample_6.csv")
data_lv2_kccq=drilldata_process_kccq(df_drilldown,'Category')

all_dimension=pd.read_csv('data/all_dimension.csv')

#for modify criteria list
dimensions = ['Age Band' , 'Gender'  , 'Patient Health Risk Level' , 'NYHA Class' , 'Medication Adherence' , 'Comorbidity Type',  'Weight Band' , 'Comorbidity Score' , 'Ejection Fraction' , 'Years Since HF Diagnosis' , 'Prior Use of ACE/ARB' ]

disable_list=['Comorbidity Type', 'Weight Band','Comorbidity Score','Ejection Fraction','Years Since HF Diagnosis','Prior Use of ACE/ARB']

#modebar display
button_to_rm=['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'hoverClosestCartesian','hoverCompareCartesian','hoverClosestGl2d', 'hoverClosestPie', 'toggleHover','toggleSpikelines']



def col_content_drilldown_kccq(app):
	return html.Div(
			[
                dbc.Row(
					[
						dbc.Col(card_overview_drilldown_kccq(18),width=8),
						dbc.Col(card_key_driver_drilldown_kccq(app),width=4),
					]
				),
#				card_confounding_factors_kccq(app),
                html.Div(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Div(
                                        [
                                            html.H2("Performance Drilldown", style={"font-size":"3rem"}),
                                            html.H3("check table view for more details...", style={"font-size":"1rem"}),
                                        ],
                                        style={"padding-left":"2rem"}
                                    ), width=8),
                                dbc.Col(modal_drilldown_tableview(), width=4)
                            ]
                        )
                    ],
                    style={"padding-bottom":"1rem", "padding-top":"2rem"}
                ),
                html.Div(
                    dbc.Tabs(
                        [
                            dbc.Tab(tab_patient_analysis_kccq(app), label="Patient Analysis", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
#                            dbc.Tab(tab_physician_analysis_kccq(app), label="Physician Analysis", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
                        ], 
                        # id = 'tab_container'
                    ),
                )
				
			]
		)


def card_overview_drilldown_kccq(percentage):
    if percentage < 10:
        color = "#dc3545"
        condition = "worse than target"
    elif percentage <20:
        color = "#1357DD"
        condition = "same as target"
    else:
        color = "#28a745"
        condition = "better than target"

    return html.Div(
			[
				dbc.Row(
                        [
                            dbc.Col(html.H1("KCCQ Score (Patient Reported Outcome)", style={"font-size":"1.6rem"}), width="auto"),
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H3("Improvement from Baseline", style={"font-size":"0.8rem", "color":"#fff"}),
                                        html.H2(str(percentage)+" points", style={"font-size":"1.2rem", "margin-top":"-9px", "color":"#fff"}),
                                    ],
                                    style={"margin-top":"-20px"}
                                ),
                                style={"height":"2.5rem", "border":"none", "background-color":color, "text-align":"center", "margin-top":"-6px"},
                            ),
                        ],
                        style={"padding-left":"1rem"}
                    ),
                html.P("As of June 30th.", style={"color":"#000", "font-size":"0.8rem","padding-left":"1rem"}),
                dbc.Row(
                    [
                        dbc.Col(
                            [   html.H1("KCCQ Score Performance Year Results", style={"font-size":"1.6rem"}),
                                html.Div(
                                    [
                                        dcc.Graph(figure=barchart_kccq(df_drill_barchart_kccq),config={'modeBarButtonsToRemove': button_to_rm,'displaylogo': False,},style={"height":"28rem"}),
                                    ]
                                )
                            ],
                            width=7,
                            style={"height":"10rem"}
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [   html.H1("Patient Distribution by Improvement Level", style={"font-size":"1.6rem"}),
                                        html.H3("Risk Adjustment Details", style={"font-size":"0.8rem","margin-top":"-1.8rem","color":"#919191","background-color":"#f5f5f5","width":"9rem","padding-left":"1rem","padding-right":"1rem","text-align":"center"}),
                                        html.Div([dcc.Graph(figure=piechart_kccq(df_drill_piechart_kccq),style={"height":"24rem","padding-bottom":"1rem"},config={'modeBarButtonsToRemove': button_to_rm,'displaylogo': False,})]),
                                    ],
                                    style={"border-radius":"0.5rem","border":"2px solid #d2d2d2","padding":"1rem","height":"25.5rem"}
                                )
                            ],
                            width=4,
                            
                        )
                    ],
                ),
            ],
		)


def card_key_driver_drilldown_kccq(app):
	return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
		                        dbc.Col(html.H4("Patient Cohort with Least Improvement (bottom 3)", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),
                        
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div([gaugegraph_kccq(df_driver_kccq,0)], style={"padding-top":"1.5rem"}),
                                        html.Div(html.H4("{:.1f} ".format(abs(df_driver_kccq['%'][0])),style={"color":"#ff4d17"}), style={"margin-top":"-1.5rem","text-align":"center","font-size":"1rem","color":"#ffeb78"}),
                                    ],
                                    width=6),
                                dbc.Col(
                                    [
                                        html.Div([gaugegraph_kccq(df_driver_kccq,1)], style={"padding-top":"1.5rem"}),
                                        html.Div(html.H4("{:.1f}".format(abs(df_driver_kccq['%'][1])),style={"color":'rgba(246,177,17,1)'}), style={"margin-top":"-1.5rem","text-align":"center","font-size":"1rem","color":"#aeff78"}),
                                    ],
                                    width=6),
                                dbc.Col(
                                    [
                                        html.Div([gaugegraph_kccq(df_driver_kccq,2)], style={"padding-top":"1.5rem"}),
                                        html.Div(html.H4("{:.1f}".format(abs(df_driver_kccq['%'][2])),style={"color":'rgba(246,177,17,1)'}), style={"margin-top":"-1.5rem","text-align":"center","font-size":"1rem","color":"#39db44"}),
                                    ],
                                    width=6),

                                
                            ],
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )



def card_confounding_factors_kccq(app):
	return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("Confounding Factors Unaccounted for in the Contract", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),
                        
                        dbc.Row(
                            [
                               
                                dbc.Col(element_confounding_factors_kccq(0.003, "Benefit Change")),
                                dbc.Col(element_confounding_factors_kccq(-0.002, "Outlier Impact")),
                            ],
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )


def element_confounding_factors_kccq(percentage, factor):
    if percentage > 0:
        color = "success"
    elif percentage == 0:
        color = "secondary"
    else:
        color = "danger"

    return dbc.Row(
            [
                dbc.Col(dbc.Badge(str(abs(percentage*100))+"%", color=color, className="mr-1"), width="auto", style={"font-family":"NotoSans-SemiBold"}),
                dbc.Col(html.H6(factor, style = {"font-size":"1rem", "padding-top":"0.1rem"})),
            ],
            style={"padding":"1rem"}
        )


def tab_patient_analysis_kccq(app):
    return html.Div(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                card_graph1_patient_performance_drilldown_kccq(app),
                                
                                

                    html.Hr(),

                                card_table1_patient_performance_drilldown_kccq(app),

                                
                            ]
                        ),
                        className="mb-3",
                        style={"border":"none", "border-radius":"0.5rem"}
                    ),

                    
                ]
            )


def tab_physician_analysis_kccq(app):
    return html.Div(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                card_graph2_physician_performance_drilldown_kccq(app),
                                
                                

                    html.Hr(),

                                card_table1_physician_performance_drilldown_kccq(app),

                                
                            ]
                        ),
                        className="mb-3",
                        style={"border":"none", "border-radius":"0.5rem"}
                    ),

                    
                ]
            )

def mod_criteria_button_kccq():
    return [
                                dbc.Button(
                                    "Click to modify criteria",
                                    id="button-mod-dim-lv1-kccq",
                                    className="mb-3",
                                    style={"background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Regular", "font-size":"0.8rem"},
                                ),
                                dbc.Popover([
                                    dbc.PopoverHeader("Modify criteria"),
                                    dbc.PopoverBody([
                                        html.Div(
                                            [
                                                dbc.RadioItems(
                                                    options = [{'label':c , 'value':c,'disabled' : False} if c not in disable_list else {'label':c , 'value':c,'disabled' : True} for c in dimensions
                                                              ],
                                                    value = "Medication Adherence",
                                                    labelCheckedStyle={"color": "#057aff"},
                                                    id = "list-dim-lv1-kccq",
                                                    style={"font-family":"NotoSans-Condensed", "font-size":"0.8rem", "padding":"1rem"},
                                                ),
                                            ],
                                            style={"padding-top":"0.5rem", "padding-bottom":"2rem"}
                                        )
                                         
                                       
                                        
                                    ]
                                    ),
                                ],
                                id = "popover-mod-dim-lv1-kccq",
                                is_open = False,
                                target = "button-mod-dim-lv1-kccq",
                                placement = "top",
                                ),
                                
                            ]


def card_graph1_patient_performance_drilldown_kccq(app):
	return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("Performance Drilldown by Patient Cohort", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),
                        
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H1("By Medication Adherence",id='dimname_on_patient_lv1_kccq', style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"0.8rem"}), width=9),
                                                dbc.Col(mod_criteria_button_kccq(), style={"padding-top":"0.8rem"}),
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ), 
                                
                                html.Div(drillgraph_lv1_kccq(drilldata_process_kccq(df_drilldown,'Medication Adherence'),'dashtable_patient_lv1_kccq','Medication Adherence'),id="drill_patient_lv1_kccq",style={"padding-top":"2rem","padding-bottom":"2rem"}), 
                            ], 
                            style={"max-height":"80rem"}
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )

def filter_template_kccq(dim,idname,default_val='All'):
    return(dcc.Dropdown(
                                id=idname,
                                options=[{'label': i, 'value': i} for i in all_dimension[all_dimension['dimension']==dim].loc[:,'value']],
                                value=default_val,
                                clearable=False,
                            ))

def card_table1_patient_performance_drilldown_kccq(app):
    return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("KCCQ Category Analysis", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H1("By Category", style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"1.2rem"}), width=5),
                                                dbc.Col(
                                                    [
                                                        html.Div("Medication Adherence",id="filter_patient_1_2_name_kccq", style={"font-size":"0.6rem"}),
                                                        html.Div(filter_template_kccq("Medication Adherence","filter_patient_1_2_value_kccq",default_val='All'),id="filter_patient_1_2_contain_kccq"),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=2,
                                                ),
                                                
                                                                                    
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ), 
#                                html.H4("* Default sorting: by Contribution to Overall Performance Difference", style={"font-size":"0.8rem","color":"#919191","padding-top":"1rem","margin-bottom":"-1rem"}), 
                                html.Div([dashtable_lv3_kccq(data_lv2_kccq,'dashtable_patient_lv2_kccq')],style={"padding":"1rem"})
                            ], 
                            style={"max-height":"120rem"}
                        ),
                        

                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )



if __name__ == "__main__":
    app.run_server(host="127.0.0.1",debug=True)









