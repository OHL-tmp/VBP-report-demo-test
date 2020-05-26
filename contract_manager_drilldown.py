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





def create_layout(app):
#    load_data()
    return html.Div(
                [ 
                    html.Div([Header_mgmt(app, False, True, False, False)], style={"height":"6rem"}, className = "sticky-top navbar-expand-lg"),
                    
                    html.Div(
                        [
                            col_content_drilldown(app),
                        ],
                        className="mb-3",
                        style={"padding-left":"3rem", "padding-right":"3rem","padding-top":"1rem"},
                    ),
                    
                ],
                style={"background-color":"#f5f5f5"},
            )


def col_menu_drilldown():

	return html.Div(
				[
                    dbc.Row(
                        [
                            dbc.Col(html.Hr(className="ml-1", style={"background-color":"#1357DD"})),
                            dbc.Col(dropdownmenu_select_measures(), width="auto"),
                            dbc.Col(html.Hr(className="ml-1", style={"background-color":"#1357DD"})),
                            #dbc.Col(card_selected_measures(),)
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div()),
                            dbc.Col(html.H6("click to change measure", style={"font-size":"0.6rem"}), width="auto"),
                            dbc.Col(html.Div()),
                            #dbc.Col(card_selected_measures(),)
                        ]
                    )
				],
                style={"padding":"0.5rem"}
			)


def dropdownmenu_select_measures():
	return dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem("Volume Based Measures", header=True),
                    dbc.DropdownMenuItem("YTD Market Share %"),
                    dbc.DropdownMenuItem("Utilizer Count"),
                    dbc.DropdownMenuItem("Avg Script(30-day adj) per Utilizer"),
                    dbc.DropdownMenuItem("Total Script Count (30-day-adj) by Dosage (in thousand)"),
                    dbc.DropdownMenuItem("Total Units by Dosage (in thousand)"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Value Based Measures", header=True),
                    dbc.DropdownMenuItem("CHF Related Average Cost per Patient", disabled=True),
                    dbc.DropdownMenuItem("CHF Related Hospitalization Rate"),
                    dbc.DropdownMenuItem("NT - proBNP Change %"),
                    dbc.DropdownMenuItem("LVEF LS Mean Change %"),
                    dbc.DropdownMenuItem(divider=True),
                    html.P(
                        "Select measure to drill.",
                    style={"padding-left":"1rem", "font-size":"0.6rem"}),
                ],
                label="CHF Related Average Cost per Patient",
                toggle_style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem","border-radius":"5rem","background-color":"#1357DD"},
            )

def card_selected_measures():
	return html.Div(
			[
				html.H2("Current measure : Value Based Measures - CHF Related Average Cost per Patient", style={"font-size":"1.5rem"})
			],
		)



def col_content_drilldown(app):
	return html.Div(
			[
                html.Div([html.Div([col_menu_drilldown()], style={"border-radius":"5rem","background-color":"none"})], style={"padding-bottom":"3rem"}),
				html.Div(div_main_content_CRACP(app)),
				
			]
		)


def div_main_content_CRACP(app):
    return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(card_overview_drilldown(0.01),width=8),
                        dbc.Col(card_key_driver_drilldown(app),width=4),
                    ]
                ),
                card_confounding_factors(app),
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
                            dbc.Tab(tab_patient_analysis(app,2), label="Patient Analysis", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
                            dbc.Tab(tab_physician_analysis(app,2), label="Physician Analysis", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
                        ], 
                        # id = 'tab_container'
                    ),
                )
            ]
        )


def div_main_content_CRHR(app):
    return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(card_overview_drilldown(0.01),width=8),
                        dbc.Col(card_key_driver_drilldown(app),width=4),
                    ]
                ),
                card_confounding_factors(app),
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
                            dbc.Tab(tab_patient_analysis(app,1), label="Patient Analysis", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
                            dbc.Tab(tab_physician_analysis(app,1), label="Physician Analysis", style={"background-color":"#fff"}, tab_style={"font-family":"NotoSans-Condensed"}),
                        ], 
                        # id = 'tab_container'
                    ),
                )
            ]
        )


def card_overview_drilldown(percentage):
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
                            dbc.Col(html.H1("CHF Related Average Cost per Patient", style={"font-size":"1.6rem"}), width="auto"),
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


def card_key_driver_drilldown(app):
	return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
		                        dbc.Col(html.H4("Key Drivers", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                                dbc.Col([dbc.Button("See All Drivers", id = 'button-all-driver',
                                                        style={"background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Regular", "font-size":"0.6rem"},
                                                    ),
                                        dbc.Modal([
                                                dbc.ModalHeader("All Drivers"),
                                                dbc.ModalBody(children = html.Div([table_driver_all(df_driver_all)], style={"padding":"1rem"})),
                                                dbc.ModalFooter(
                                                        dbc.Button("Close", id = 'close-all-driver',
                                                                        style={"background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Regular", "font-size":"0.8rem"},
                                                                    )
                                                        )
                                                ], id = 'modal-all-driver', size="lg")],
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
                                        html.Div(html.H4("{:.1f} %".format(df_driver['%'][0]*100),style={"color":"#ff4d17"}), style={"margin-top":"-1.5rem","text-align":"center","font-size":"1rem","color":"#ffeb78"}),
                                    ],
                                    width=6),
                                dbc.Col(
                                    [
                                        html.Div([gaugegraph(df_driver,1)], style={"padding-top":"1.5rem"}),
                                        html.Div(html.H4("{:.1f} %".format(df_driver['%'][1]*100),style={"color":"#ffeb78"}), style={"margin-top":"-1.5rem","text-align":"center","font-size":"1rem","color":"#aeff78"}),
                                    ],
                                    width=6),
                                dbc.Col(
                                    [
                                        html.Div([gaugegraph(df_driver,2)], style={"padding-top":"1.5rem"}),
                                        html.Div(html.H4("{:.1f} %".format(df_driver['%'][2]*100),style={"color":"#ffeb78"}), style={"margin-top":"-1.5rem","text-align":"center","font-size":"1rem","color":"#39db44"}),
                                    ],
                                    width=6),
                                
                            ],
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )



def card_confounding_factors(app):
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
                                dbc.Col(element_confounding_factors(-0.002, "Change in Covered Services"), width=3),
                                dbc.Col(element_confounding_factors(0.003, "Benefit Change"), width=3),
                                dbc.Col(element_confounding_factors(-0.002, "Provider Contracting Change"), width=3),
                                dbc.Col(element_confounding_factors(-0.002, "Outlier Impact"), width=3),
                            ],
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )


def element_confounding_factors(percentage, factor):
    if percentage > 0:
        color = "danger"
    elif percentage == 0:
        color = "secondary"
    else:
        color = "success"

    return dbc.Row(
            [
                dbc.Col(dbc.Badge(str(percentage*100)+"%", color=color, className="mr-1"), width=3, style={"font-family":"NotoSans-SemiBold"}),
                dbc.Col(html.H6(factor, style = {"font-size":"1rem", "padding-top":"0.1rem"}), width=9),
            ],
            style={"padding":"1rem"}
        )


def tab_patient_analysis(app, n):
    if n == 2:
        body = [
                    card_graph1_performance_drilldown(app),

                    html.Hr(),

                    card_table1_performance_drilldown(app),

                    html.Hr(),

                    card_table2_performance_drilldown(app),
                    
                ]
    elif n == 1:
        body = [
                    card_graph1_performance_drilldown(app),

                    html.Hr(),

                    card_table1_performance_drilldown(app)
                ]
    else:
        body = [
                    card_graph1_performance_drilldown(app),
                  
                ]
    return html.Div(
                [
                    dbc.Card(
                        dbc.CardBody(
                            body
                        ),
                        className="mb-3",
                        style={"border":"none", "border-radius":"0.5rem"}
                    ),

                    
                ]
            )


def tab_physician_analysis(app,n):
    if n == 2:
        body = [
                    card_graph2_performance_drilldown(app),

                    html.Hr(),

                    card_table1_performance_drilldown(app),

                    html.Hr(),

                    card_table2_performance_drilldown(app),
                    
                ]
    elif n == 1:
        body = [
                    card_graph2_performance_drilldown(app),

                    html.Hr(),

                    card_table1_performance_drilldown(app)
                ]
    else:
        body = [
                    card_graph2_performance_drilldown(app),
                  
                ]
    return html.Div(
                [
                    dbc.Card(
                        dbc.CardBody(
                            body
                        ),
                        className="mb-3",
                        style={"border":"none", "border-radius":"0.5rem"}
                    ),

                    
                ]
            )


def card_graph1_performance_drilldown(app):
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
                                                dbc.Col(html.H1("By Comorbidity Type",id='dimname_on_lv1', style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"0.8rem"}), width=9),
                                                dbc.Col(mod_criteria_button(), style={"padding-top":"0.8rem"}),
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ), 
                                html.Div(drillgraph_lv1(drilldata_process(df_drilldown,'Patient Health Risk Level'),'dashtable_lv1','Patient Health Risk Level'),id="drill_lv1",style={"padding-top":"2rem","padding-bottom":"2rem"}), 
                            ], 
                            style={"max-height":"80rem"}
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )

def mod_criteria_button():
    return [
                                dbc.Button(
                                    "Click to modify criteria",
                                    id="button-mod-dim-lv1",
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
                                                    value = "Patient Health Risk Level",
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
                                id = "popover-mod-dim-lv1",
                                is_open = False,
                                target = "button-mod-dim-lv1",
                                placement = "top",
                                ),
                                
                            ]
    

    
def card_graph2_performance_drilldown(app):
	return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("Performance Drilldown by Managing physician Group", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H1("By Physician Group", style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"1.2rem"}), width=6),
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            html.Div(html.H4("Risk Score Band"),id="filter1_2_name", style={"font-size":"0.8rem"}),
                                                            html.Div(filter_template("Risk Score Band","filter1_2_value",default_val='All')),
                                                        ]
                                                    ), 
                                                    style={"padding":"0.8rem"},
                                                    width=5,
                                                ),
                                            ]
                                        )
                                    ],
                                    style={"padding-left":"2rem","padding-right":"1rem","border-radius":"5rem","background-color":"#f7f7f7","margin-top":"2rem"}
                                ), 
                                html.Div(drillgraph_lv1(drilldata_process(df_drilldown,'Managing Physician (Group)'),'dashtable_lv2','Managing Physician (Group)'),id="drill_lv2",style={"padding-top":"2rem","padding-bottom":"2rem"}), 
                            ], 
                            style={"max-height":"80rem"}
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )

def filter_template(dim,idname,default_val='All'):
    return(dcc.Dropdown(
                                id=idname,
                                options=[{'label': i, 'value': i} for i in all_dimension[all_dimension['dimension']==dim].loc[:,'value']],
                                value=default_val,
                                clearable=False,
                            ))

def card_table1_performance_drilldown(app):
	return dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url("bullet-round-blue.png"), width="10px"), width="auto", align="start", style={"margin-top":"-4px"}),
                                dbc.Col(html.H4("Performance Drilldown by Service Categories", style={"font-size":"1rem", "margin-left":"10px"}), width=8),
                            ],
                            no_gutters=True,
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H1("By Service Categories", style={"color":"#f0a800", "font-size":"1.5rem","padding-top":"1.2rem"}), width=5),
                                                dbc.Col( 
                                                    [
                                                        html.Div("Risk Score Band",id="filter1_3_name", style={"font-size":"0.8rem"}),
                                                        html.Div(filter_template("Risk Score Band","filter1_3_value",default_val='All')),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=3,
                                                ),
                                                dbc.Col( 
                                                    [
                                                        html.Div("Managing Physician (Group)",id="filter2_3_name", style={"font-size":"0.8rem"}),
                                                        html.Div(filter_template("Managing Physician (Group)","filter2_3_value",default_val='All')),
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
                                html.Div([dashtable_lv3(data_lv3,'Service Category','dashtable_lv3',1)],id="drill_lv3",style={"padding":"1rem"}),
                            ], 
                            style={"max-height":"80rem"}
                        ),
                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )



def card_table2_performance_drilldown(app):
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
                                                        html.Div("Risk Score Band",id="filter1_4_name", style={"font-size":"0.6rem"}),
                                                        html.Div(filter_template("Risk Score Band","filter1_4_value",default_val='All')),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Div("Managing Physician (Group)",id="filter2_4_name", style={"font-size":"0.6rem"}),
                                                        html.Div(filter_template("Managing Physician (Group)","filter2_4_value",default_val='All')),
                                                    ], 
                                                    style={"padding":"0.8rem"},
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Div("Service Category",id="filter3_4_name", style={"font-size":"0.6rem"}),
                                                        html.Div(filter_template("Service Category","filter3_4_value",default_val='All')),
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
                                html.Div([dashtable_lv3(data_lv4,'Sub Category','dashtable_lv4',0)],id="drill_lv4",style={"padding":"1rem"})
                            ], 
                            style={"max-height":"120rem"}
                        ),
                        

                    ]
                ),
                className="mb-3",
                style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)", "border":"none", "border-radius":"0.5rem"}
            )

layout = create_layout(app)

@app.callback(
    Output("modal-all-driver","is_open"),
    [Input("button-all-driver","n_clicks"),
     Input("close-all-driver","n_clicks")],
    [State("modal-all-driver","is_open")]        
)
def open_all_driver(n1,n2,is_open):
    if n1 or n2:
        return not is_open
    return is_open



# modify lv1 criteria
@app.callback(
    Output("popover-mod-dim-lv1","is_open"),
    [Input("button-mod-dim-lv1","n_clicks"),],
   # Input("mod-button-mod-measure","n_clicks"),
    [State("popover-mod-dim-lv1", "is_open")],
)
def toggle_popover_mod_criteria(n1, is_open):
    if n1 :
        return not is_open
    return is_open

#update lv1 table and filter1 on following page based on criteria button
@app.callback(
   [ Output("drill_lv1","children"),
     Output("filter1_2_name","children"),
     Output("filter1_2_value","options"),
     Output("filter1_3_name","children"),
     Output("filter1_3_value","options"),
     Output("filter1_4_name","children"),
     Output("filter1_4_value","options"), 
     Output("dimname_on_lv1","children"),
   ],
   [Input("list-dim-lv1","value")] 
)
def update_table_dimension(dim):
    f1_name=dim
    filter1_value_list=[{'label': i, 'value': i} for i in all_dimension[all_dimension['dimension']==dim].loc[:,'value']]
    
    return drillgraph_lv1(drilldata_process(df_drilldown,dim),'dashtable_lv1',dim),f1_name,filter1_value_list,f1_name,filter1_value_list,f1_name,filter1_value_list,'By '+f1_name

#update filter1 on following page based on selected columns

@app.callback(
   [ Output("filter1_2_value","value"),   
     Output("filter1_3_value","value"),  
     Output("filter1_4_value","value"),  
   ],
   [ Input("dashtable_lv1","selected_columns"),
   ] 
)
def update_filter1value(col):
    if col==[]:
        col_1='All'
    else:col_1=col[0]        
    
    return col_1,col_1,col_1

#update filter2 on following page based on selected columns

@app.callback(
   [ Output("filter2_3_value","value"),   
     Output("filter2_4_value","value"),  
   ],
   [ Input("dashtable_lv2","selected_columns"),
   ] 
)
def update_filter2value(col):
    if col==[]:
        col_1='All'
    else:col_1=col[0]        
    
    return col_1,col_1

#update filter3 on following page based on selected rows

@app.callback(
   Output("filter3_4_value","value"),   
   [Input("dashtable_lv3","selected_row_ids"),
    Input("dashtable_lv3","data"),
   ] 
)
def update_filter3value(row,data):
    
    if row is None or row==[]:
        row_1='All'
    else:
        row_1=row[0]  
    return row_1
    
#update lv2 on filter1

@app.callback(
    Output("drill_lv2","children"),    
   [ Input("filter1_2_name","children"),
     Input("filter1_2_value","value"),
   ] 
)
def update_table2(dim,val):       
    
    return drillgraph_lv1(drilldata_process(df_drilldown,'Managing Physician (Group)',dim1=dim,f1=val),'dashtable_lv2','Managing Physician (Group)')


#update lv3 on filter1,filter2

@app.callback(
   Output("dashtable_lv3","data"), 
   [ Input("filter1_3_name","children"),
     Input("filter1_3_value","value"),
     Input("filter2_3_name","children"),
     Input("filter2_3_value","value"),
     Input('dashtable_lv3', 'sort_by'),
   ] 
)
def update_table3(dim1,val1,dim2,val2,sort_dim):
    #global data_lv3
    
    data_lv3=drilldata_process(df_drilldown,'Service Category',dim1,val1,dim2,val2)       
    #data_lv3.to_csv('data/overall_performance.csv')
    if sort_dim==[]:
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv3[0:len(data_lv3)-1].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv3[len(data_lv3)-1:len(data_lv3)]])
    df1['id']=df1[df1.columns[0]]
    df1.set_index('id', inplace=True, drop=False)
    return df1.to_dict('records')



#update lv4 on filter1,filter2,filter3

@app.callback(
    Output("dashtable_lv4","data"),    
   [ Input("filter1_4_name","children"),
     Input("filter1_4_value","value"),
     Input("filter2_4_name","children"),
     Input("filter2_4_value","value"),
     Input("filter3_4_name","children"),
     Input("filter3_4_value","value"),
     Input('dashtable_lv4', 'sort_by'),
   ] 
)
def update_table4(dim1,val1,dim2,val2,dim3,val3,sort_dim):
    
    #global data_lv4
    data_lv4=drilldata_process(df_drilldown,'Sub Category',dim1,val1,dim2,val2,dim3,val3)   
    
    if sort_dim==[]:
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv4[0:len(data_lv4)-2].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv4[len(data_lv4)-2:len(data_lv4)]])
    
    return df1.to_dict('records')


#sort lv3 on selected dimension
'''@app.callback(
    Output('drill_lv3', "children"),
    [ Input('dashtable_lv3', 'sort_by'),],
)
def sort_table3(sort_dim):
    if sort_dim==[]:
        df1=data_lv3
    else:    
        df1=data_lv3[0:len(data_lv3)-1].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
        df1=pd.concat([df1,data_lv3[len(data_lv3)-1:len(data_lv3)]])
        #df1['id']=df1[df1.columns[0]]
        #df1.set_index('id', inplace=True, drop=False)
    
    return [dashtable_lv3(df1,'Service Category','dashtable_lv3',0)]'''


#### callback ####

## modal
@app.callback(
    Output("drilldown-modal-centered", "is_open"),
    [Input("drilldown-open-centered", "n_clicks"), Input("drilldown-close-centered", "n_clicks")],
    [State("drilldown-modal-centered", "is_open")],
)
def toggle_modal_dashboard_domain_selection(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    [Output('dimension_filter_1', 'options'),
    Output('dimension_filter_1', 'value'),
    Output('dimension_filter_1', 'multi')],
    [Input('dimension_filter_selection_1', 'value')]
    )
def filter_dimension_1(v):
    if v:
        if v == 'Service Category':
            return [{"label": 'All', "value": 'All'}]+[{"label": k, "value": k} for k in list(filter_list.keys())], 'All', False
        else:
            return [{"label": k, "value": k} for k in dimension[v]], dimension[v], True
    return [], [], True


@app.callback(
    [Output('dimension_filter_2', 'options'),
    Output('dimension_filter_2', 'value'),
    Output('dimension_filter_2', 'multi')],
    [Input('dimension_filter_selection_1', 'value'),
    Input('dimension_filter_selection_2', 'value'),
    Input('dimension_filter_1', 'value')]
    )
def filter_dimension_1(v1, v2, v3):
    if v2:
        if v2 == 'Service Category':
            return [{"label": 'All', "value": 'All'}]+[{"label": k, "value": k} for k in list(filter_list.keys())], 'All', False
        elif v1 == 'Service Category' and v2 == 'Sub Category':
            sub_filter = filter_list[v3]
            if v3 == 'All':
                return [], 'All', False
            return [{"label": k, "value": k} for k in sub_filter], sub_filter, True
        else:
            return [{"label": k, "value": k} for k in dimension[v2]], dimension[v2], True
    return [], [], True

    
@app.callback(
    Output('dropdown-dimension-2','clearable'),
    [Input('dropdown-dimension-3','value')]
    )
def dropdown_clear(v):
    if v:
        return False
    return True

@app.callback(
    [Output('dropdown-dimension-2','options'),
    Output('dropdown-dimension-2','disabled')],
    [Input('dropdown-dimension-1','value')]
    )
def dropdown_menu_2(v):
    if v is None:
        return [], True
    elif v == 'Service Category':
        dropdown_option = [{"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys()) if len(dimension[k]) != 0] + [{"label": 'Service Category', "value": 'Service Category', 'disabled' : True}, {"label": 'Sub Category', "value": 'Sub Category'}] + [{"label": k, "value": k, 'disabled' : True} for k in list(dimension.keys()) if len(dimension[k]) == 0]
        return dropdown_option, False
    else:
        dropdown_option = [{"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys()) if len(dimension[k]) != 0 and k != v] + [{"label": 'Service Category', "value": 'Service Category'}, {"label": 'Sub Category', "value": 'Sub Category', 'disabled' : True}] + [{"label": k, "value": k, 'disabled' : True} for k in list(dimension.keys()) if len(dimension[k]) == 0 or k ==v]
        return dropdown_option, False

@app.callback(
    [Output('dropdown-dimension-3','options'),
    Output('dropdown-dimension-3','disabled')],
    [Input('dropdown-dimension-1','value'),
    Input('dropdown-dimension-2','value')]
    )
def dropdown_menu_3(v1, v2):
    v = [v1, v2]
    if v2 is None:
        return [], True
    elif 'Service Category' in v and 'Sub Category' not in v:
        dropdown_option = [{"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys()) if len(dimension[k]) != 0] + [{"label": 'Service Category', "value": 'Service Category', 'disabled' : True}, {"label": 'Sub Category', "value": 'Sub Category'}] + [{"label": k, "value": k, 'disabled' : True} for k in list(dimension.keys()) if len(dimension[k]) == 0]
        return dropdown_option, False
    elif 'Service Category' in v and 'Sub Category' in v:
        dropdown_option =  [{"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys()) if len(dimension[k]) != 0] + [{"label": 'Service Category', "value": 'Service Category', 'disabled' : True}, {"label": 'Sub Category', "value": 'Sub Category', 'disabled' : True}] + [{"label": k, "value": k, 'disabled' : True} for k in list(dimension.keys()) if len(dimension[k]) == 0]
        return dropdown_option, False
    else:
        dropdown_option = [{"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys()) if len(dimension[k]) != 0 and k not in v] + [{"label": 'Service Category', "value": 'Service Category'}, {"label": 'Sub Category', "value": 'Sub Category', 'disabled' : True}] + [{"label": k, "value": k, 'disabled' : True} for k in list(dimension.keys()) if len(dimension[k]) == 0 or k in v]
        return dropdown_option, False

@app.callback(
    [Output('dimension_filter_selection_2', 'options'),
    Output('dimension_filter_selection_2', 'disabled')],
    [Input('dimension_filter_selection_1', 'value'),
    Input('dimension_filter_1', 'value')]
    )
def filter_menu_2(v, f):
    if v is None:
        return [], True
    elif v == 'Service Category':
        if f =='All':
            dropdown_option = [{"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys()) if len(dimension[k]) != 0] + [{"label": 'Service Category', "value": 'Service Category', 'disabled' : True}, {"label": 'Sub Category', "value": 'Sub Category', 'disabled' : True}] + [{"label": k, "value": k, 'disabled' : True} for k in list(dimension.keys()) if len(dimension[k]) == 0]
            return dropdown_option, False
        else:
            dropdown_option = [{"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys()) if len(dimension[k]) != 0] + [{"label": 'Service Category', "value": 'Service Category', 'disabled' : True}, {"label": 'Sub Category', "value": 'Sub Category'}] + [{"label": k, "value": k, 'disabled' : True} for k in list(dimension.keys()) if len(dimension[k]) == 0]
            return dropdown_option, False
    else:
        dropdown_option = [{"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys()) if len(dimension[k]) != 0 and k != v] + [{"label": 'Service Category', "value": 'Service Category'}, {"label": 'Sub Category', "value": 'Sub Category', 'disabled' : True}] + [{"label": k, "value": k, 'disabled' : True} for k in list(dimension.keys()) if len(dimension[k]) == 0 or k ==v]
        return dropdown_option, False

@app.callback(
    [Output('datatable-tableview', "columns"),
    Output('datatable-tableview', "data")],
    [Input('dropdown-dimension-1','value'),
    Input('dropdown-dimension-2','value'),
    Input('dropdown-dimension-3','value'),
    Input('dimension_filter_selection_1','value'),
    Input('dimension_filter_selection_2','value'),
    Input('dimension_filter_1','value'),
    Input('dimension_filter_2','value'),
    Input('dropdown-measure-1', 'value')]
    )
def datatable_data_selection(v1, v2, v3, d1, d2, f1, f2, m):
    if d1:
        if d1 == 'Service Category':
            if d2 is None:
                if f1 == 'All':
                    df_drilldown_filtered = df_drilldown
                    cate_cnt = cate_mix_cnt
                else:
                    df_drilldown_filtered = df_drilldown[df_drilldown['Service Category'].isin([f1])]
                    cate_cnt = len(filter_list[f1])
            elif f1 != 'All' and d2 == 'Sub Category':
                df_drilldown_filtered = df_drilldown[(df_drilldown['Service Category'].isin([f1])) & (df_drilldown['Sub Category'].isin(f2))]
                cate_cnt = len(f2)
            else:
                df_drilldown_filtered = df_drilldown[df_drilldown[d2].isin(f2)]
                if f1 == 'All':
                    cate_cnt = cate_mix_cnt
                else:
                    cate_cnt = len(filter_list[f1])
        elif d2 == 'Service Category':
            if f2 == 'All':
                df_drilldown_filtered = df_drilldown[df_drilldown[d1].isin(f1)]
                cate_cnt = cate_mix_cnt
            else:
                df_drilldown_filtered = df_drilldown[(df_drilldown['Service Category'].isin([f2])) & (df_drilldown[d1].isin(f1))]
                cate_cnt = len(filter_list[f2])
        else:
            if d2:
                df_drilldown_filtered = df_drilldown[(df_drilldown[d1].isin(f1)) & (df_drilldown[d2].isin(f2))]
                cate_cnt = cate_mix_cnt
            else: 
                df_drilldown_filtered = df_drilldown[df_drilldown[d1].isin(f1)]
                cate_cnt = cate_mix_cnt
    else:
        df_drilldown_filtered = df_drilldown
        cate_cnt = cate_mix_cnt

    table_column = []
    selected_dimension = []
    if v1 is not None:
        selected_dimension.append(v1)
    if v2 is not None:
        selected_dimension.append(v2)
    if v3 is not None:
        selected_dimension.append(v3)

    table_column.extend(list(set(selected_dimension + ['Service Category', 'Sub Category'])))
    table_column.append("Pt Count")
    percent_list = ['Diff % from Benchmark Utilization', 'Diff % from Benchmark Total Cost', 'Diff % from Benchmark Unit Cost', 'Patient %']
    dollar_list = ['YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost', 'YTD Unit Cost', 'Annualized Unit Cost', 'Benchmark Unit Cost']
    if len(selected_dimension) > 0:
#        ptct_dimension = set(selected_dimension + ['Service Category', 'Sub Category'])
        table_column.extend(measure_ori) 
        df_agg_pre = df_drilldown_filtered[table_column].groupby(by = list(set(selected_dimension + ['Service Category', 'Sub Category']))).sum().reset_index()
        df_agg = df_agg_pre[table_column].groupby(by = selected_dimension).agg({'Pt Count':'mean', 'YTD Utilization':'sum', 'Annualized Utilization':'sum', 'Benchmark Utilization':'sum', 
            'YTD Total Cost':'sum', 'Annualized Total Cost':'sum', 'Benchmark Total Cost':'sum'}).reset_index()
#        df_agg['Pt Count'] = df_agg['Pt Count']/cate_cnt
        df_agg['Patient %'] = df_agg['Pt Count']/995000
        df_agg['YTD Utilization'] = df_agg['YTD Utilization']/df_agg['Pt Count']
        df_agg['Annualized Utilization'] = df_agg['Annualized Utilization']/df_agg['Pt Count']
        df_agg['Benchmark Utilization'] = df_agg['Benchmark Utilization']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Utilization'] = (df_agg['Annualized Utilization'] - df_agg['Benchmark Utilization'])/df_agg['Benchmark Utilization']
        df_agg['YTD Total Cost'] = df_agg['YTD Total Cost']/df_agg['Pt Count']
        df_agg['Annualized Total Cost'] = df_agg['Annualized Total Cost']/df_agg['Pt Count']
        df_agg['Benchmark Total Cost'] = df_agg['Benchmark Total Cost']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Total Cost'] = (df_agg['Annualized Total Cost'] - df_agg['Benchmark Total Cost'])/df_agg['Benchmark Total Cost']
        df_agg['YTD Unit Cost'] = df_agg['YTD Total Cost']/df_agg['YTD Utilization']
        df_agg['Annualized Unit Cost'] = df_agg['Annualized Total Cost']/df_agg['Annualized Utilization']
        df_agg['Benchmark Unit Cost'] = df_agg['Benchmark Total Cost']/df_agg['Benchmark Utilization']
        df_agg['Diff % from Benchmark Unit Cost'] = (df_agg['Annualized Unit Cost'] - df_agg['Benchmark Unit Cost'])/df_agg['Benchmark Unit Cost']
#        df_agg.style.format({'Diff % from Target Utilization' : "{:.2%}", 'Diff % from Target Total Cost': "{:.2%}", 'Diff % from Target Unit Cost' : "{:.2%}"})
#        df_agg.reset_index(inplace = True)
        show_column = selected_dimension + ['Patient %'] + m 
        if 'Diff % from Benchmark Total Cost' in m:
            df_agg =  df_agg[show_column].sort_values(by =  'Diff % from Benchmark Total Cost', ascending =False)
        else:
            df_agg = df_agg[show_column]
    else:
        show_column = ['Patient %'] + m 
        df_agg = df_drilldown_filtered[show_column]
    
    
    return [{"name": i, "id": i, "selectable":True,"type":"numeric", "format": FormatTemplate.percentage(1)} if i in percent_list else {"name": i, "id": i, "selectable":True, "type":"numeric","format": FormatTemplate.money(0)} if i in dollar_list else {"name": i, "id": i, "selectable":True, "type":"numeric","format": Format(precision=1, scheme = Scheme.fixed)} for i in show_column], df_agg.to_dict('records')




if __name__ == "__main__":
    app.run_server(host="127.0.0.1",debug=True)









