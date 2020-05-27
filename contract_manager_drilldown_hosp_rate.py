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

from modal_drilldown_tableview import *

from app import app

df_drilldown=pd.read_csv("data/drilldown_sample_6.csv")
#dimensions=df_drilldown.columns[0:12]
df_drill_waterfall=pd.read_csv("data/drilldown waterfall graph.csv")
df_driver=pd.read_csv("data/Drilldown Odometer.csv")
df_driver_all=pd.read_csv("data/Drilldown All Drivers.csv")
data_lv3=drilldata_process(df_drilldown,'Service Category')
data_lv4=drilldata_process(df_drilldown,'Sub Category')

all_dimension=[]
for i in list(df_drilldown.columns[0:14]):
    all_dimension.append([i,'All'])
    for j in list(df_drilldown[i].unique()):
        all_dimension.append([i,j])
all_dimension=pd.DataFrame(all_dimension,columns=['dimension','value'])

#for modify criteria list
dimensions = ['Age Band' , 'Gender'  , 'Patient Health Risk Level' , 'NYHA Class' , 'Medication Adherence' , 'Comorbidity Type',  'Weight Band' , 'Comorbidity Score' , 'Ejection Fraction' , 'Years Since HF Diagnosis' , 'Prior Use of ACE/ARB' ]

disable_list=['Comorbidity Type', 'Weight Band','Comorbidity Score','Ejection Fraction','Years Since HF Diagnosis','Prior Use of ACE/ARB']

#modebar display
button_to_rm=['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'hoverClosestCartesian','hoverCompareCartesian','hoverClosestGl2d', 'hoverClosestPie', 'toggleHover','toggleSpikelines']



def col_content_drilldown_crhr(app):
	return html.Div(
			[
                dbc.Row(
					[
						dbc.Col(card_overview_drilldown_crhr(0.012),width=8),
						dbc.Col(card_key_driver_drilldown_crhr(app),width=4),
					]
				),
				card_confounding_factors_crhr(app),
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
                            dbc.Tab(tab_patient_analysis_crhr(app), label="Patient Analysis", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
                            dbc.Tab(tab_physician_analysis_crhr(app), label="Physician Analysis", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
                        ], 
                        # id = 'tab_container'
                    ),
                )
				
			]
		)


def card_overview_drilldown_crhr(percentage):
    if percentage > 0:
        color = "#dc3545"
        condition = "worse than target"
    elif percentage == 0:
        color = "#1357DD"
        condition = "same as target"
    else:
        color = "#28a745"
        condition = "better than target"

    return html.Div(
			[
				dbc.Row(
                        [
                            dbc.Col(html.H1("CHF Related Hospitalization Rate", style={"font-size":"1.6rem"}), width="auto"),
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H3("worse than target", style={"font-size":"0.8rem", "color":"#fff"}),
                                        html.H2(str(percentage*100)+"%", style={"font-size":"1.2rem", "margin-top":"-9px", "color":"#fff"}),
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
                            [
                                html.Div(
                                    [
                                        dcc.Graph(figure=drill_bar(df_drill_waterfall),config={'modeBarButtonsToRemove': button_to_rm,'displaylogo': False,}),
                                    ]
                                )
                            ],
                            width=7,
                            style={"height":"10rem"}
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H3("Risk Adjustment Details", style={"font-size":"0.8rem","margin-top":"-1.8rem","color":"#919191","background-color":"#f5f5f5","width":"9rem","padding-left":"1rem","padding-right":"1rem","text-align":"center"}),
                                        html.Div([dcc.Graph(figure=drill_waterfall(df_drill_waterfall),style={"height":"24rem","padding-bottom":"1rem"},config={'modeBarButtonsToRemove': button_to_rm,'displaylogo': False,})]),
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


def card_key_driver_drilldown_crhr(app):
	return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
		                        dbc.Col(html.H4("Key Drivers", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                                dbc.Col([dbc.Button("See All Drivers", id = 'button-all-driver-crhr',
                                                        style={"background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Regular", "font-size":"0.6rem"},
                                                    ),
                                        dbc.Modal([
                                                dbc.ModalHeader("All Drivers"),
                                                dbc.ModalBody(children = html.Div([table_driver_all(df_driver_all)], style={"padding":"1rem"})),
                                                dbc.ModalFooter(
                                                        dbc.Button("Close", id = 'close-all-driver-crhr',
                                                                        style={"background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Regular", "font-size":"0.8rem"},
                                                                    )
                                                        )
                                                ], id = 'modal-all-driver-crhr', size="lg")],
                                        width=3,
                                        ),
                            ],
                            no_gutters=True,
                        ),
                        
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div([gaugegraph(df_driver,0)], style={"padding-top":"1.5rem"}),
                                        html.Div(html.H4("{:.1f} %".format(abs(df_driver['%'][0]*100)),style={"color":"#ff4d17"}), style={"margin-top":"-1.5rem","text-align":"center","font-size":"1rem","color":"#ffeb78"}),
                                    ],
                                    width=6),
                                dbc.Col(
                                    [
                                        html.Div([gaugegraph(df_driver,1)], style={"padding-top":"1.5rem"}),
                                        html.Div(html.H4("{:.1f} %".format(abs(df_driver['%'][1]*100)),style={"color":"#ff4d17"}), style={"margin-top":"-1.5rem","text-align":"center","font-size":"1rem","color":"#aeff78"}),
                                    ],
                                    width=6),
                                dbc.Col(
                                    [
                                        html.Div([gaugegraph(df_driver,2)], style={"padding-top":"1.5rem"}),
                                        html.Div(html.H4("{:.1f} %".format(abs(df_driver['%'][2]*100)),style={"color":"#18cc75"}), style={"margin-top":"-1.5rem","text-align":"center","font-size":"1rem","color":"#39db44"}),
                                    ],
                                    width=6),
                                
                            ],
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )



def card_confounding_factors_crhr(app):
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
                                dbc.Col(element_confounding_factors_crhr(-0.002, "Change in Covered Services"), width=3),
                                dbc.Col(element_confounding_factors_crhr(0.003, "Benefit Change"), width=3),
                                dbc.Col(element_confounding_factors_crhr(-0.002, "Provider Contracting Change"), width=3),
                                dbc.Col(element_confounding_factors_crhr(-0.002, "Outlier Impact"), width=3),
                            ],
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )


def element_confounding_factors_crhr(percentage, factor):
    if percentage > 0:
        color = "success"
    elif percentage == 0:
        color = "secondary"
    else:
        color = "danger"

    return dbc.Row(
            [
                dbc.Col(dbc.Badge(str(abs(percentage*100))+"%", color=color, className="mr-1"), width=3, style={"font-family":"NotoSans-SemiBold"}),
                dbc.Col(html.H6(factor, style = {"font-size":"1rem", "padding-top":"0.1rem"}), width=9),
            ],
            style={"padding":"1rem"}
        )


def tab_patient_analysis_crhr(app):
    return html.Div(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                card_graph1_patient_performance_drilldown_crhr(app),
                                
                                

                    html.Hr(),

                                card_table1_patient_performance_drilldown_crhr(app),

                    html.Hr(),

                                card_table2_patient_performance_drilldown_crhr(app),
                                
                            ]
                        ),
                        className="mb-3",
                        style={"border":"none", "border-radius":"0.5rem"}
                    ),

                    
                ]
            )


def tab_physician_analysis_crhr(app):
    return html.Div(
                [
                    dbc.Card(
                        dbc.CardBody(
                            [
                                card_graph2_physician_performance_drilldown_crhr(app),
                                
                                

                    html.Hr(),

                                card_table1_physician_performance_drilldown_crhr(app),

                    html.Hr(),

                                card_table2_physician_performance_drilldown_crhr(app),
                                
                            ]
                        ),
                        className="mb-3",
                        style={"border":"none", "border-radius":"0.5rem"}
                    ),

                    
                ]
            )

def mod_criteria_button_crhr():
    return [
                                dbc.Button(
                                    "Click to modify criteria",
                                    id="button-mod-dim-lv1-crhr",
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
                                                    id = "list-dim-lv1",
                                                    style={"font-family":"NotoSans-Condensed", "font-size":"0.8rem", "padding":"1rem"},
                                                ),
                                            ],
                                            style={"padding-top":"0.5rem", "padding-bottom":"2rem"}
                                        )
                                         
                                       
                                        
                                    ]
                                    ),
                                ],
                                id = "popover-mod-dim-lv1-crhr",
                                is_open = False,
                                target = "button-mod-dim-lv1-crhr",
                                placement = "top",
                                ),
                                
                            ]


def card_graph1_patient_performance_drilldown_crhr(app):
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
                                                dbc.Col(html.H1("By Medication Adherence",id='dimname_on_patient_lv1_crhr', style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"0.8rem"}), width=9),
                                                dbc.Col(mod_criteria_button_crhr(), style={"padding-top":"0.8rem"}),
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ), 
                                
                                html.Div(drillgraph_lv1(drilldata_process(df_drilldown,'Medication Adherence'),'dashtable_patient_lv1_crhr','Medication Adherence'),id="drill_patient_lv1_crhr",style={"padding-top":"2rem","padding-bottom":"2rem"}), 
                            ], 
                            style={"max-height":"80rem"}
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )



def filter_template_crhr(dim,idname,default_val='All'):
    return(dcc.Dropdown(
                                id=idname,
                                options=[{'label': i, 'value': i} for i in all_dimension[all_dimension['dimension']==dim].loc[:,'value']],
                                value=default_val,
                                clearable=False,
                            ))

def card_table1_patient_performance_drilldown_crhr(app):
    return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("Performance Drilldown by Service Category", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H1("By Service Category", style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"1.2rem"}), width=5),
                                                dbc.Col( 
                                                    [
                                                        html.Div("Medication Adherence",id="filter_patient_1_2_name_crhr", style={"font-size":"0.8rem"}),
                                                        html.Div(filter_template_crhr("Medication Adherence","filter_patient_1_2_value_crhr",default_val='All')),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=3,
                                                ),
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ),
                                html.H4("* Default sorting: by Contribution to Overall Performance Difference", style={"font-size":"0.8rem","color":"#919191","padding-top":"1rem","margin-bottom":"-1rem"}), 
                                html.Div([dashtable_lv3(data_lv3,'Service Category','dashtable_patient_lv2_crhr',1)],id="drill_patient_lv2",style={"padding":"1rem"}),
                            ], 
                            style={"max-height":"80rem"}
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )



def card_table2_patient_performance_drilldown_crhr(app):
    return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("Service Category Drilldown by Sub Category", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H1("By Sub Category", style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"1.2rem"}), width=5),
                                                
                                                dbc.Col(
                                                    [
                                                        html.Div("Medication Adherence",id="filter_patient_1_3_name_crhr", style={"font-size":"0.6rem"}),
                                                        html.Div(filter_template_crhr("Medication Adherence","filter_patient_1_3_value_crhr",default_val='All')),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Div("Service Category",id="filter_patient_2_3_name", style={"font-size":"0.6rem"}),
                                                        html.Div(filter_template_crhr("Service Category","filter_patient_2_3_value_crhr",default_val='All')),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=2,
                                                ),
                                    
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ), 
                                html.H4("* Default sorting: by Contribution to Overall Performance Difference", style={"font-size":"0.8rem","color":"#919191","padding-top":"1rem","margin-bottom":"-1rem"}), 
                                html.Div([dashtable_lv3(data_lv4,'Sub Category','dashtable_patient_lv3_crhr',0)],id="drill_patient_lv3",style={"padding":"1rem"})
                            ], 
                            style={"max-height":"120rem"}
                        ),
                        

                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )

def card_graph2_physician_performance_drilldown_crhr(app):
    return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("Performance Drilldown by Managing Physician (Group)", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H1("By Managing Physician (Group)", style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"1.2rem"}), width=6),
                                                
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ), 
                                html.Div(drillgraph_lv1(drilldata_process(df_drilldown,'Managing Physician (Group)'),'dashtable_physician_lv1_crhr','Managing Physician (Group)'),id="drill_physician_lv1",style={"padding-top":"2rem","padding-bottom":"2rem"}), 
                            ], 
                            style={"max-height":"80rem"}
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )


def card_table1_physician_performance_drilldown_crhr(app):
	return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("Performance Drilldown by Service Category", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H1("By Service Category", style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"1.2rem"}), width=5),
                                                
                                                dbc.Col( 
                                                    [
                                                        html.Div("Managing Physician (Group)",id="filter_physician_1_2_name_crhr", style={"font-size":"0.8rem"}),
                                                        html.Div(filter_template_crhr("Managing Physician (Group)","filter_physician_1_2_value_crhr",default_val='All')),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=3,
                                                )
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ),
                                html.H4("* Default sorting: by Contribution to Overall Performance Difference", style={"font-size":"0.8rem","color":"#919191","padding-top":"1rem","margin-bottom":"-1rem"}), 
                                html.Div([dashtable_lv3(data_lv3,'Service Category','dashtable_physician_lv2_crhr',1)],id="drill_physician_lv2",style={"padding":"1rem"}),
                            ], 
                            style={"max-height":"80rem"}
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )



def card_table2_physician_performance_drilldown_crhr(app):
	return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("Service Category Drilldown by Sub Category", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H1("By Sub Category", style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"1.2rem"}), width=5),
                                                
                                                dbc.Col(
                                                    [
                                                        html.Div("Managing Physician (Group)",id="filter_physician_1_3_name_crhr", style={"font-size":"0.6rem"}),
                                                        html.Div(filter_template_crhr("Managing Physician (Group)","filter_physician_1_3_value_crhr",default_val='All')),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Div("Service Category",id="filter_physician_2_3_name_crhr", style={"font-size":"0.6rem"}),
                                                        html.Div(filter_template_crhr("Service Category","filter_physician_2_3_value_crhr",default_val='All')),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=2,
                                                ),
                                    
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ), 
                                html.H4("* Default sorting: by Contribution to Overall Performance Difference", style={"font-size":"0.8rem","color":"#919191","padding-top":"1rem","margin-bottom":"-1rem"}), 
                                html.Div([dashtable_lv3(data_lv4,'Sub Category','dashtable_physician_lv3_crhr',0)],id="drill_physician_lv3",style={"padding":"1rem"})
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









