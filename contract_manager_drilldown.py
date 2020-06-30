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

from contract_manager_drilldown_hosp_rate import *
from contract_manager_drilldown_avg_cost import *
from contract_manager_drilldown_kccq import *


from modal_drilldown_tableview import *
from modal_drilldown_tableview_crhr import *
from modal_drilldown_tableview_kccq import *


from app import app
#app = dash.Dash(__name__)
#server = app.server

df_drilldown=pd.read_csv("data/drilldown_sample_6.csv")
#dimensions=df_drilldown.columns[0:12]
df_drill_waterfall=pd.read_csv("data/drilldown waterfall graph.csv")
df_driver=pd.read_csv("data/Drilldown Odometer.csv")
df_driver_all=pd.read_csv("data/Drilldown All Drivers.csv")
data_lv3=drilldata_process(df_drilldown,'Service Category')
data_lv4=drilldata_process(df_drilldown,'Sub Category')

all_dimension=pd.read_csv('data/all_dimension.csv')

#for modify criteria list
dimensions = ['Age Band' , 'Gender'  , 'Patient Health Risk Level' , 'NYHA Class' , 'Medication Adherence' , 'Comorbidity Type',  'Weight Band' , 'Comorbidity Score' , 'Ejection Fraction' , 'Years Since HF Diagnosis' , 'Prior Use of ACE/ARB' ]

disable_list=['Comorbidity Type', 'Weight Band','Comorbidity Score','Ejection Fraction','Years Since HF Diagnosis','Prior Use of ACE/ARB']

#modebar display
button_to_rm=['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'hoverClosestCartesian','hoverCompareCartesian','hoverClosestGl2d', 'hoverClosestPie', 'toggleHover','toggleSpikelines']


def reshape_drilldowndata(df):
    df1 = pd.melt(df, 
        id_vars = ['Age Band', 'Gender', 'Weight Band', 'Comorbidity Type',
       'Comorbidity Score', 'Patient Health Risk Level', 'NYHA Class',
       'Ejection Fraction', 'Years Since HF Diagnosis', 'Prior Use of ACE/ARB',
       'Medication Adherence', 'Managing Physician (Group)',
       'Service Category', 'Sub Category', 'Pt Count', 'YTD Utilization',
       'Annualized Utilization', 'Benchmark Utilization', 'YTD Total Cost',
       'Annualized Total Cost', 'Benchmark Total Cost',], 
        value_vars = ['KCCQ BL PL Score',
       'KCCQ BL SF Score', 'KCCQ BL QL Score', 'KCCQ BL SL Score',
       'KCCQ BL ALL Score'], var_name = 'KCCQ Category', value_name = 'Baseline Average KCCQ Score')
    df1['KCCQ Category'] = df1['KCCQ Category'].apply(lambda x: 'Physical Limitation' if x == 'KCCQ BL PL Score' else ('Symptom Frequency' if x == 'KCCQ BL SF Score' else ('Quality of Life' if x == 'KCCQ BL QL Score' else ('Social Limitation' if x == 'KCCQ BL SL Score' else 'ALL'))))

    df2 = pd.melt(df, 
        id_vars = ['Age Band', 'Gender', 'Weight Band', 'Comorbidity Type',
       'Comorbidity Score', 'Patient Health Risk Level', 'NYHA Class',
       'Ejection Fraction', 'Years Since HF Diagnosis', 'Prior Use of ACE/ARB',
       'Medication Adherence', 'Managing Physician (Group)',
       'Service Category', 'Sub Category', 'Pt Count', 'YTD Utilization',
       'Annualized Utilization', 'Benchmark Utilization', 'YTD Total Cost',
       'Annualized Total Cost', 'Benchmark Total Cost',], 
        value_vars = ['KCCQ YTD PL Score',
       'KCCQ YTD SF Score', 'KCCQ YTD QL Score', 'KCCQ YTD SL Score',
       'KCCQ YTD ALL Score'], var_name = 'KCCQ Category', value_name = 'YTD Average KCCQ Score')
    df2['KCCQ Category'] = df2['KCCQ Category'].apply(lambda x: 'Physical Limitation' if x == 'KCCQ YTD PL Score' else ('Symptom Frequency' if x == 'KCCQ YTD SF Score' else ('Quality of Life' if x == 'KCCQ YTD QL Score' else ('Social Limitation' if x == 'KCCQ YTD SL Score' else 'ALL'))))

    df_reshape = pd.merge(df1, df2, how = 'left', on = ['Age Band', 'Gender', 'Weight Band', 'Comorbidity Type',
       'Comorbidity Score', 'Patient Health Risk Level', 'NYHA Class',
       'Ejection Fraction', 'Years Since HF Diagnosis', 'Prior Use of ACE/ARB',
       'Medication Adherence', 'Managing Physician (Group)',
       'Service Category', 'Sub Category', 'Pt Count', 'YTD Utilization',
       'Annualized Utilization', 'Benchmark Utilization', 'YTD Total Cost',
       'Annualized Total Cost', 'Benchmark Total Cost','KCCQ Category'])
    return df_reshape

df_drilldown_reshape = reshape_drilldowndata(df_drilldown)

def create_layout(app):
#    load_data()
    return html.Div(
                [ 
                    html.Div([Header_mgmt(app, False, True, False, False)], style={"height":"6rem"}, className = "sticky-top navbar-expand-lg"),
                    
                    html.Div([html.Div([col_menu_drilldown()], style={"border-radius":"5rem","background-color":"none"})], style={"padding-bottom":"3rem"}),
                
                    html.Div(
                        [
                            html.Div(col_content_drilldown(app), id='drilldown-div-avgcost-container', hidden=False),
                            html.Div(col_content_drilldown_crhr(app), id='drilldown-div-crhr-container', hidden=True),
                            html.Div(col_content_drilldown_kccq(app), id='drilldown-div-kccq-container', hidden=True),
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
                    dbc.DropdownMenuItem("YTD Market Share %", disabled=True),
                    dbc.DropdownMenuItem("Utilizer Count", disabled=True),
                    dbc.DropdownMenuItem("Avg Script(30-day adj) per Utilizer", disabled=True),
                    dbc.DropdownMenuItem("Total Script Count (30-day-adj) by Dosage (in thousand)", disabled=True),
                    dbc.DropdownMenuItem("Total Units by Dosage (in thousand)", disabled=True),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Value Based Measures", header=True),
                    dbc.DropdownMenuItem("CHF Related Average Cost per Patient", id="avg_cost"),
                    dbc.DropdownMenuItem("CHF Related Hospitalization Rate", id="crhr"),
                    dbc.DropdownMenuItem("KCCQ-12 Score", id="kccq"),
                    dbc.DropdownMenuItem("NT - proBNP Change %", disabled=True),
                    dbc.DropdownMenuItem("LVEF LS Mean Change %", disabled=True),
                    dbc.DropdownMenuItem(divider=True),
                    html.P(
                        "Select measure to drill.",
                    style={"padding-left":"1rem", "font-size":"0.6rem"}),
                ],
                id="drilldown-dropdownmenu",
                label="CHF Related Average Cost per Patient",
                toggle_style={"font-family":"NotoSans-SemiBold","font-size":"1.2rem","border-radius":"5rem","background-color":"#1357DD"},
            )

def card_selected_measures():
	return html.Div(
			[
				html.H2("Current measure : Value Based Measures - CHF Related Average Cost per Patient", style={"font-size":"1.5rem"})
			],
		)



layout = create_layout(app)
#app.layout = create_layout(app)

##### select drilldown #####

@app.callback(
    [
    Output('drilldown-dropdownmenu','label'),
    Output('drilldown-div-avgcost-container', 'hidden'),
    Output('drilldown-div-crhr-container', 'hidden'),
    Output('drilldown-div-kccq-container', 'hidden')],
    [
        Input("avg_cost", "n_clicks"),
        Input("crhr", "n_clicks"),
        Input("kccq", "n_clicks"),
    ],
)
def select_drilldown(*args):
    state_avg_cost = True
    state_crhr = True
    state_kccq = True

    ctx = dash.callback_context

    if not ctx.triggered:
        state_avg_cost = False
        button_id = "avg_cost"
        label = "CHF Related Average Cost per Patient"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "crhr":
            state_crhr = False
            label = "CHF Related Hospitalization Rate"
        elif button_id == "avg_cost":
            state_avg_cost = False
            label = "CHF Related Average Cost per Patient"
        elif button_id == "kccq":
            state_kccq = False
            label = "KCCQ-12 Score"


    return label, state_avg_cost, state_crhr, state_kccq





##### avg_cost callbacks #####

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

#update patient lv1 table and filter1 on following page based on criteria button
@app.callback(
   [ Output("drill_patient_lv1","children"),
     Output("filter_patient_1_2_name","children"),
     Output("filter_patient_1_2_contain","children"),
     Output("filter_patient_1_3_name","children"),
     Output("filter_patient_1_3_contain","children"),
     Output("dimname_on_patient_lv1","children"),
   ],
   [Input("list-dim-lv1","value")] 
)
def update_table_dimension(dim):
    f1_name=dim
#    filter1_value_list=[{'label': i, 'value': i} for i in all_dimension[all_dimension['dimension']==dim].loc[:,'value']]
#    filter1=filter_template(dim,"filter_patient_1_2_value")
    
    return drillgraph_lv1(drilldata_process(df_drilldown,dim),'dashtable_patient_lv1',dim),f1_name,filter_template(dim,"filter_patient_1_2_value"),f1_name,filter_template(dim,"filter_patient_1_3_value"),'By '+f1_name

#update patient filter1 on following page based on selected rows

@app.callback(
   [ Output("filter_patient_1_2_value","value"),   
     Output("filter_patient_1_3_value","value"),    ],
   [ Input("dashtable_patient_lv1","selected_row_ids"),
   ] 
)
def update_filter1value_patient(row):

    if row is None or row==[]:
        row_1='All'
    else:row_1=row[0]        
    
    return row_1,row_1

#update patient filter2 on following page based on selected rows

@app.callback(
    Output("filter_patient_2_3_value","value"),   
   [ Input("dashtable_patient_lv2","selected_row_ids"),
   ] 
)
def update_filter2value(row):
    if row is None or row==[]:
        row_1='All'
    else:row_1=row[0]        
    
    return row_1


#update patient lv1 on sort_by

@app.callback(
   Output("dashtable_patient_lv1","data"), 
   [ Input('dashtable_patient_lv1', 'sort_by'),
   ] ,
   [State('dashtable_patient_lv1', 'data')]
)
def update_table3(sort_dim,data):
    #global data_lv3
    
    data_lv3=pd.DataFrame(data)       
    #data_lv3.to_csv('data/overall_performance.csv')
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv3[0:len(data_lv3)-1].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv3[len(data_lv3)-1:len(data_lv3)]])
    df1['id']=df1[df1.columns[0]]
    df1.set_index('id', inplace=True, drop=False)
    return df1.to_dict('records')

#update patient lv2 on sort_by

@app.callback(
   Output("dashtable_patient_lv2","data"), 
   [ Input("filter_patient_1_2_name","children"),
     Input("filter_patient_1_2_value","value"),
     Input('dashtable_patient_lv2', 'sort_by'),
   ] 
)
def update_table3(dim1,val1,sort_dim):
    #global data_lv3
    
    data_lv3=drilldata_process(df_drilldown,'Service Category',dim1,val1)       
    #data_lv3.to_csv('data/overall_performance.csv')
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv3[0:len(data_lv3)-1].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv3[len(data_lv3)-1:len(data_lv3)]])
    df1['id']=df1[df1.columns[0]]
    df1.set_index('id', inplace=True, drop=False)
    return df1.to_dict('records')



#update patient lv3 on filter1,filter2

@app.callback(
    Output("dashtable_patient_lv3","data"),    
   [ Input("filter_patient_1_3_name","children"),
     Input("filter_patient_1_3_value","value"),
     Input("filter_patient_2_3_name","children"),
     Input("filter_patient_2_3_value","value"),
     Input('dashtable_patient_lv3', 'sort_by'),
   ] 
)
def update_table4(dim1,val1,dim2,val2,sort_dim):
    
    #global data_lv4
    data_lv4=drilldata_process(df_drilldown,'Sub Category',dim1,val1,dim2,val2)   
    
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv4[0:len(data_lv4)-2].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv4[len(data_lv4)-2:len(data_lv4)]])
    
    return df1.to_dict('records')



#update physician filter1 on following page based on selected rows

@app.callback(
   [ Output("filter_physician_1_2_value","value"),   
     Output("filter_physician_1_3_value","value"),    ],
   [ Input("dashtable_physician_lv1","selected_row_ids"),
   ] 
)
def update_filter1value(row):

    if row is None or row==[]:
        row_1='All'
    else:row_1=row[0]        
    
    return row_1,row_1

#update physician filter2 on following page based on selected columns

@app.callback(
    Output("filter_physician_2_3_value","value"),   
   [ Input("dashtable_physician_lv2","selected_row_ids"),
   ] 
)
def update_filter2value(row):
    if row is None or row==[]:
        row_1='All'
    else:row_1=row[0]        
    
    return row_1


#update physician lv1 on sort_by

@app.callback(
   Output("dashtable_physician_lv1","data"), 
   [ Input('dashtable_physician_lv1', 'sort_by'),
   ] ,
   [State('dashtable_physician_lv1', 'data')]
)
def update_table3(sort_dim,data):

    data_lv3=pd.DataFrame(data)
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv3[0:len(data_lv3)-1].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv3[len(data_lv3)-1:len(data_lv3)]])
    df1['id']=df1[df1.columns[0]]
    df1.set_index('id', inplace=True, drop=False)
    return df1.to_dict('records')

#update physician lv2 on sort_by

@app.callback(
   Output("dashtable_physician_lv2","data"), 
   [ Input("filter_physician_1_2_name","children"),
     Input("filter_physician_1_2_value","value"),
     Input('dashtable_physician_lv2', 'sort_by'),
   ] 
)
def update_table3(dim1,val1,sort_dim):

    
    data_lv3=drilldata_process(df_drilldown,'Service Category',dim1,val1)     
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv3[0:len(data_lv3)-1].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv3[len(data_lv3)-1:len(data_lv3)]])
    df1['id']=df1[df1.columns[0]]
    df1.set_index('id', inplace=True, drop=False)
    return df1.to_dict('records')



#update physician lv3 on filter1,filter2

@app.callback(
    Output("dashtable_physician_lv3","data"),    
   [ Input("filter_physician_1_3_name","children"),
     Input("filter_physician_1_3_value","value"),
     Input("filter_physician_2_3_name","children"),
     Input("filter_physician_2_3_value","value"),
     Input('dashtable_physician_lv3', 'sort_by'),
   ] 
)
def update_table4(dim1,val1,dim2,val2,sort_dim):
    
    #global data_lv4
    data_lv4=drilldata_process(df_drilldown,'Sub Category',dim1,val1,dim2,val2)   
    
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv4[0:len(data_lv4)-2].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv4[len(data_lv4)-2:len(data_lv4)]])
    
    return df1.to_dict('records')    



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
    Output('dropdown-measure-1', 'options'),
    [Input('dropdown-dimension-1','value'),
    Input('dropdown-dimension-2','value'),
    Input('dropdown-dimension-3','value')]
    )
def update_measures(d1, d2, d3):
    d = [d1, d2, d3]
    measure_kccq = ['YTD Utilization per Thousand', 'Annualized Utilization per Thousand', 'Benchmark Utilization per Thousand', 'Diff % from Benchmark Utilization per Thousand',
        'YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost', 'Diff % from Benchmark Total Cost',
        'YTD Unit Cost', 'Annualized Unit Cost', 'Benchmark Unit Cost', 'Diff % from Benchmark Unit Cost',
        'YTD Hospitalization Rate per Thousand', 'Annualized Hospitalization Rate per Thousand', 'Benchmark Hospitalization Rate per Thousand', 'Diff % from Benchmark Hospitalization Rate per Thousand',
        'Baseline Average KCCQ Score', 'YTD Average KCCQ Score', 'KCCQ Improvement from Baseline']
    if 'KCCQ Category' in d:
        return [{"label": k, "value": k} for k in measure_kccq]
    else:
        return [{"label": k, "value": k} for k in measure]

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
                    df_drilldown_filtered = df_drilldown_reshape
                    cate_cnt = cate_mix_cnt
                else:
                    df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape['Service Category'].isin([f1])]
                    cate_cnt = len(filter_list[f1])
            elif f1 != 'All' and d2 == 'Sub Category':
                df_drilldown_filtered = df_drilldown_reshape[(df_drilldown_reshape['Service Category'].isin([f1])) & (df_drilldown_reshape['Sub Category'].isin(f2))]
                cate_cnt = len(f2)
            else:
                df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape[d2].isin(f2)]
                if f1 == 'All':
                    cate_cnt = cate_mix_cnt
                else:
                    cate_cnt = len(filter_list[f1])
        elif d2 == 'Service Category':
            if f2 == 'All':
                df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape[d1].isin(f1)]
                cate_cnt = cate_mix_cnt
            else:
                df_drilldown_filtered = df_drilldown_reshape[(df_drilldown_reshape['Service Category'].isin([f2])) & (df_drilldown_reshape[d1].isin(f1))]
                cate_cnt = len(filter_list[f2])
        else:
            if d2:
                df_drilldown_filtered = df_drilldown_reshape[(df_drilldown_reshape[d1].isin(f1)) & (df_drilldown_reshape[d2].isin(f2))]
                cate_cnt = cate_mix_cnt
            else: 
                df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape[d1].isin(f1)]
                cate_cnt = cate_mix_cnt
    else:
        df_drilldown_filtered = df_drilldown_reshape
        cate_cnt = cate_mix_cnt

    df_drilldown_filtered['YTD IP Utilization'] = df_drilldown_filtered.apply(lambda x: x['YTD Utilization'] if x['Service Category'] == 'Inpatient' else 0, axis = 1)
    df_drilldown_filtered['Annualized IP Utilization'] = df_drilldown_filtered.apply(lambda x: x['Annualized Utilization'] if x['Service Category'] == 'Inpatient' else 0, axis = 1)
    df_drilldown_filtered['Benchmark IP Utilization'] = df_drilldown_filtered.apply(lambda x: x['Benchmark Utilization'] if x['Service Category'] == 'Inpatient' else 0, axis = 1)

    table_column = []
    selected_dimension = []
    if v1 is not None:
        selected_dimension.append(v1)
    if v2 is not None:
        selected_dimension.append(v2)
    if v3 is not None:
        selected_dimension.append(v3)

    table_column.extend(list(set(selected_dimension + ['Service Category', 'Sub Category', 'KCCQ Category'])))
    table_column.append("Pt Count")
    percent_list = ['Diff % from Benchmark Utilization per Thousand', 'Diff % from Benchmark Total Cost', 'Diff % from Benchmark Unit Cost', 'Patient %', 'Diff % from Benchmark Hospitalization Rate per Thousand']
    dollar_list = ['YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost', 'YTD Unit Cost', 'Annualized Unit Cost', 'Benchmark Unit Cost']
    if len(selected_dimension) > 0:

        table_column.extend(measure_ori) 
        df_agg_pre = df_drilldown_filtered[table_column].groupby(by = list(set(selected_dimension + ['Service Category', 'Sub Category', 'KCCQ Category']))).sum().reset_index()
        df_agg = df_agg_pre[table_column].groupby(by = selected_dimension).agg({'Pt Count':'mean', 'YTD Utilization':'sum', 'Annualized Utilization':'sum', 'Benchmark Utilization':'sum', 
            'YTD Total Cost':'sum', 'Annualized Total Cost':'sum', 'Benchmark Total Cost':'sum', 'YTD IP Utilization':'sum', 'Annualized IP Utilization':'sum', 'Benchmark IP Utilization':'sum',
            'Baseline Average KCCQ Score':'mean', 'YTD Average KCCQ Score':'mean'}).reset_index()

        df_agg['Patient %'] = df_agg['Pt Count']/995000
        df_agg['YTD Utilization per Thousand'] = 1000 * df_agg['YTD Utilization']/df_agg['Pt Count']
        df_agg['Annualized Utilization per Thousand'] = 1000 * df_agg['Annualized Utilization']/df_agg['Pt Count']
        df_agg['Benchmark Utilization per Thousand'] = 1000 * df_agg['Benchmark Utilization']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Utilization per Thousand'] = (df_agg['Annualized Utilization'] - df_agg['Benchmark Utilization'])/df_agg['Benchmark Utilization']
        df_agg['YTD Total Cost'] = df_agg['YTD Total Cost']/df_agg['Pt Count']
        df_agg['Annualized Total Cost'] = df_agg['Annualized Total Cost']/df_agg['Pt Count']
        df_agg['Benchmark Total Cost'] = df_agg['Benchmark Total Cost']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Total Cost'] = (df_agg['Annualized Total Cost'] - df_agg['Benchmark Total Cost'])/df_agg['Benchmark Total Cost']
        df_agg['YTD Unit Cost'] = df_agg['YTD Total Cost']/df_agg['YTD Utilization']
        df_agg['Annualized Unit Cost'] = 1000 * df_agg['Annualized Total Cost']/df_agg['Annualized Utilization']
        df_agg['Benchmark Unit Cost'] = 1000 * df_agg['Benchmark Total Cost']/df_agg['Benchmark Utilization']
        df_agg['Diff % from Benchmark Unit Cost'] = (df_agg['Annualized Unit Cost'] - df_agg['Benchmark Unit Cost'])/df_agg['Benchmark Unit Cost']
        df_agg['YTD Hospitalization Rate per Thousand'] = 1000 * df_agg['YTD IP Utilization']/df_agg['Pt Count']
        df_agg['Annualized Hospitalization Rate per Thousand'] = 1000 * df_agg['Annualized IP Utilization']/df_agg['Pt Count']
        df_agg['Benchmark Hospitalization Rate per Thousand'] = 1000 * df_agg['Benchmark IP Utilization']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Hospitalization Rate per Thousand'] = (df_agg['Annualized IP Utilization'] - df_agg['Benchmark IP Utilization'])/df_agg['Benchmark IP Utilization']

        df_agg['Baseline Average KCCQ Score'] = df_agg['Baseline Average KCCQ Score']/df_agg['Pt Count']
        df_agg['YTD Average KCCQ Score'] = df_agg['YTD Average KCCQ Score']/df_agg['Pt Count']
        df_agg['KCCQ Improvement from Baseline'] = df_agg['YTD Average KCCQ Score'] - df_agg['Baseline Average KCCQ Score']

        show_column = selected_dimension + ['Patient %'] + m 
        if 'Diff % from Benchmark Total Cost' in m:
            df_agg =  df_agg[show_column].sort_values(by =  'Diff % from Benchmark Total Cost', ascending =False)
        else:
            df_agg = df_agg[show_column]
    else:
        show_column = ['Patient %'] + m 
        df_agg = df_drilldown_filtered[show_column]
    
    
    return [{"name": i, "id": i, "selectable":True,"type":"numeric", "format": FormatTemplate.percentage(1)} if i in percent_list else {"name": i, "id": i, "selectable":True, "type":"numeric","format": FormatTemplate.money(0)} if i in dollar_list else {"name": i, "id": i, "selectable":True, "type":"numeric","format": Format(precision=1, scheme = Scheme.fixed)} for i in show_column], df_agg.to_dict('records')


##### hosp_rate callbacks #####

@app.callback(
    Output("modal-all-driver-crhr","is_open"),
    [Input("button-all-driver-crhr","n_clicks"),
     Input("close-all-driver-crhr","n_clicks")],
    [State("modal-all-driver-crhr","is_open")]        
)
def open_all_driver(n1,n2,is_open):
    if n1 or n2:
        return not is_open
    return is_open



# modify lv1 criteria
@app.callback(
    Output("popover-mod-dim-lv1-crhr","is_open"),
    [Input("button-mod-dim-lv1-crhr","n_clicks"),],
   # Input("mod-button-mod-measure","n_clicks"),
    [State("popover-mod-dim-lv1-crhr", "is_open")],
)
def toggle_popover_mod_criteria(n1, is_open):
    if n1 :
        return not is_open
    return is_open

#update patient lv1 table and filter1 on following page based on criteria button
@app.callback(
   [ Output("drill_patient_lv1_crhr","children"),
     Output("filter_patient_1_2_name_crhr","children"),
     Output("filter_patient_1_2_contain_crhr","children"),
     Output("dimname_on_patient_lv1_crhr","children"),
   ],
   [Input("list-dim-lv1-crhr","value")] 
)
def update_table_dimension(dim):
    f1_name=dim
#    filter1_value_list=[{'label': i, 'value': i} for i in all_dimension[all_dimension['dimension']==dim].loc[:,'value']]
    
    
    return drillgraph_lv1_crhr(drilldata_process_crhr(df_drilldown,dim),'dashtable_patient_lv1_crhr',dim),f1_name,filter_template_crhr(dim,"filter_patient_1_2_value_crhr"),'By '+f1_name

#update patient filter1 on following page based on selected rows

@app.callback(
    Output("filter_patient_1_2_value_crhr","value"),   
   [ Input("dashtable_patient_lv1_crhr","selected_row_ids"),
   ] 
)
def update_filter1value_patient(row):

    if row is None or row==[]:
        row_1='All'
    else:row_1=row[0]        
    
    return row_1

#update patient lv1 on sort_by

@app.callback(
   Output("dashtable_patient_lv1_crhr","data"), 
   [ Input('dashtable_patient_lv1_crhr', 'sort_by'),
   ] ,
   [ State('dashtable_patient_lv1_crhr', 'data'),]
)
def update_table3(sort_dim,data):
    #global data_lv3
    
    data_lv3=pd.DataFrame(data)       
    #data_lv3.to_csv('data/overall_performance.csv')
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv3[0:len(data_lv3)-1].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv3[len(data_lv3)-1:len(data_lv3)]])

    return df1.to_dict('records')

#update patient lv2 on sort_by

@app.callback(
   Output("dashtable_patient_lv2_crhr","data"), 
   [ Input("filter_patient_1_2_name_crhr","children"),
     Input("filter_patient_1_2_value_crhr","value"),
     Input('dashtable_patient_lv2_crhr', 'sort_by'),
   ] 
)
def update_table3(dim1,val1,sort_dim):
    #global data_lv3
    
    data_lv3=drilldata_process_crhr(df_drilldown,'Sub Category',dim1,val1)       
    #data_lv3.to_csv('data/overall_performance.csv')
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv3[0:len(data_lv3)-2].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv3[len(data_lv3)-2:len(data_lv3)]])

    return df1.to_dict('records')



#update physician filter1 on following page based on selected rows

@app.callback(
    Output("filter_physician_1_2_value_crhr","value"),   
   [ Input("dashtable_physician_lv1_crhr","selected_row_ids"),
   ] 
)
def update_filter1value(row):

    if row is None or row==[]:
        row_1='All'
    else:row_1=row[0]        
    
    return row_1

#update physician lv1 on sort by

@app.callback(
   Output("dashtable_physician_lv1_crhr","data"), 
   [ Input('dashtable_physician_lv1_crhr', 'sort_by'),
   ],
   [State('dashtable_physician_lv1_crhr', 'data'),] 
)
def update_table3(sort_dim,data):

    
    data_lv3=pd.DataFrame(data)    
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv3[0:len(data_lv3)-1].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv3[len(data_lv3)-1:len(data_lv3)]])

    return df1.to_dict('records') 

#update physician lv2 on sort by

@app.callback(
   Output("dashtable_physician_lv2_crhr","data"), 
   [ Input("filter_physician_1_2_name_crhr","children"),
     Input("filter_physician_1_2_value_crhr","value"),
     Input('dashtable_physician_lv2_crhr', 'sort_by'),
   ] 
)
def update_table3(dim1,val1,sort_dim):

    
    data_lv3=drilldata_process_crhr(df_drilldown,'Sub Category',dim1,val1)     
    if (sort_dim is None) or (sort_dim==[]):
        sort_dim=[{"column_id":"Contribution to Overall Performance Difference","direction":"desc"}]
  
    df1=data_lv3[0:len(data_lv3)-2].sort_values(by=sort_dim[0]['column_id'],ascending= sort_dim[0]['direction']=='asc')
    df1=pd.concat([df1,data_lv3[len(data_lv3)-2:len(data_lv3)]])

    return df1.to_dict('records')  


@app.callback(
    Output("drilldown-modal-centered-crhr", "is_open"),
    [Input("drilldown-open-centered-crhr", "n_clicks"), Input("drilldown-close-centered-crhr", "n_clicks")],
    [State("drilldown-modal-centered-crhr", "is_open")],
)
def toggle_modal_dashboard_domain_selection(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


#### callback ####

## modal



@app.callback(
    [Output('dimension_filter_1_crhr', 'options'),
    Output('dimension_filter_1_crhr', 'value'),
    Output('dimension_filter_1_crhr', 'multi')],
    [Input('dimension_filter_selection_1_crhr', 'value')]
    )
def filter_dimension_1(v):
    if v:
        if v == 'Service Category':
            return [{"label": 'All', "value": 'All'}]+[{"label": k, "value": k} for k in list(filter_list.keys())], 'All', False
        else:
            return [{"label": k, "value": k} for k in dimension[v]], dimension[v], True
    return [], [], True


@app.callback(
    [Output('dimension_filter_2_crhr', 'options'),
    Output('dimension_filter_2_crhr', 'value'),
    Output('dimension_filter_2_crhr', 'multi')],
    [Input('dimension_filter_selection_1_crhr', 'value'),
    Input('dimension_filter_selection_2_crhr', 'value'),
    Input('dimension_filter_1_crhr', 'value')]
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
    Output('dropdown-dimension-2-crhr','clearable'),
    [Input('dropdown-dimension-3-crhr','value')]
    )
def dropdown_clear(v):
    if v:
        return False
    return True

@app.callback(
    [Output('dropdown-dimension-2-crhr','options'),
    Output('dropdown-dimension-2-crhr','disabled')],
    [Input('dropdown-dimension-1-crhr','value')]
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
    [Output('dropdown-dimension-3-crhr','options'),
    Output('dropdown-dimension-3-crhr','disabled')],
    [Input('dropdown-dimension-1-crhr','value'),
    Input('dropdown-dimension-2-crhr','value')]
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
    [Output('dimension_filter_selection_2_crhr', 'options'),
    Output('dimension_filter_selection_2_crhr', 'disabled')],
    [Input('dimension_filter_selection_1_crhr', 'value'),
    Input('dimension_filter_1_crhr', 'value')]
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
    Output('dropdown-measure-1-crhr', 'options'),
    [Input('dropdown-dimension-1-crhr','value'),
    Input('dropdown-dimension-2-crhr','value'),
    Input('dropdown-dimension-3-crhr','value')]
    )
def update_measures(d1, d2, d3):
    d = [d1, d2, d3]
    measure_kccq = ['YTD Utilization per Thousand', 'Annualized Utilization per Thousand', 'Benchmark Utilization per Thousand', 'Diff % from Benchmark Utilization per Thousand',
        'YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost', 'Diff % from Benchmark Total Cost',
        'YTD Unit Cost', 'Annualized Unit Cost', 'Benchmark Unit Cost', 'Diff % from Benchmark Unit Cost',
        'YTD Hospitalization Rate per Thousand', 'Annualized Hospitalization Rate per Thousand', 'Benchmark Hospitalization Rate per Thousand', 'Diff % from Benchmark Hospitalization Rate per Thousand',
        'Baseline Average KCCQ Score', 'YTD Average KCCQ Score', 'KCCQ Improvement from Baseline']
    if 'KCCQ Category' in d:
        return [{"label": k, "value": k} for k in measure_kccq]
    else:
        return [{"label": k, "value": k} for k in measure]

@app.callback(
    [Output('datatable-tableview-crhr', "columns"),
    Output('datatable-tableview-crhr', "data")],
    [Input('dropdown-dimension-1-crhr','value'),
    Input('dropdown-dimension-2-crhr','value'),
    Input('dropdown-dimension-3-crhr','value'),
    Input('dimension_filter_selection_1_crhr','value'),
    Input('dimension_filter_selection_2_crhr','value'),
    Input('dimension_filter_1_crhr','value'),
    Input('dimension_filter_2_crhr','value'),
    Input('dropdown-measure-1-crhr', 'value')]
    )
def datatable_data_selection(v1, v2, v3, d1, d2, f1, f2, m):
    if d1:
        if d1 == 'Service Category':
            if d2 is None:
                if f1 == 'All':
                    df_drilldown_filtered = df_drilldown_reshape
                    cate_cnt = cate_mix_cnt
                else:
                    df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape['Service Category'].isin([f1])]
                    cate_cnt = len(filter_list[f1])
            elif f1 != 'All' and d2 == 'Sub Category':
                df_drilldown_filtered = df_drilldown_reshape[(df_drilldown_reshape['Service Category'].isin([f1])) & (df_drilldown_reshape['Sub Category'].isin(f2))]
                cate_cnt = len(f2)
            else:
                df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape[d2].isin(f2)]
                if f1 == 'All':
                    cate_cnt = cate_mix_cnt
                else:
                    cate_cnt = len(filter_list[f1])
        elif d2 == 'Service Category':
            if f2 == 'All':
                df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape[d1].isin(f1)]
                cate_cnt = cate_mix_cnt
            else:
                df_drilldown_filtered = df_drilldown_reshape[(df_drilldown_reshape['Service Category'].isin([f2])) & (df_drilldown_reshape[d1].isin(f1))]
                cate_cnt = len(filter_list[f2])
        else:
            if d2:
                df_drilldown_filtered = df_drilldown_reshape[(df_drilldown_reshape[d1].isin(f1)) & (df_drilldown_reshape[d2].isin(f2))]
                cate_cnt = cate_mix_cnt
            else: 
                df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape[d1].isin(f1)]
                cate_cnt = cate_mix_cnt
    else:
        df_drilldown_filtered = df_drilldown_reshape
        cate_cnt = cate_mix_cnt

    df_drilldown_filtered['YTD IP Utilization'] = df_drilldown_filtered.apply(lambda x: x['YTD Utilization'] if x['Service Category'] == 'Inpatient' else 0, axis = 1)
    df_drilldown_filtered['Annualized IP Utilization'] = df_drilldown_filtered.apply(lambda x: x['Annualized Utilization'] if x['Service Category'] == 'Inpatient' else 0, axis = 1)
    df_drilldown_filtered['Benchmark IP Utilization'] = df_drilldown_filtered.apply(lambda x: x['Benchmark Utilization'] if x['Service Category'] == 'Inpatient' else 0, axis = 1)

    table_column = []
    selected_dimension = []
    if v1 is not None:
        selected_dimension.append(v1)
    if v2 is not None:
        selected_dimension.append(v2)
    if v3 is not None:
        selected_dimension.append(v3)

    table_column.extend(list(set(selected_dimension + ['Service Category', 'Sub Category', 'KCCQ Category'])))
    table_column.append("Pt Count")
    percent_list = ['Diff % from Benchmark Utilization per Thousand', 'Diff % from Benchmark Total Cost', 'Diff % from Benchmark Unit Cost', 'Patient %', 'Diff % from Benchmark Hospitalization Rate per Thousand']
    dollar_list = ['YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost', 'YTD Unit Cost', 'Annualized Unit Cost', 'Benchmark Unit Cost']
    if len(selected_dimension) > 0:

        table_column.extend(measure_ori) 
        df_agg_pre = df_drilldown_filtered[table_column].groupby(by = list(set(selected_dimension + ['Service Category', 'Sub Category', 'KCCQ Category']))).sum().reset_index()
        df_agg = df_agg_pre[table_column].groupby(by = selected_dimension).agg({'Pt Count':'mean', 'YTD Utilization':'sum', 'Annualized Utilization':'sum', 'Benchmark Utilization':'sum', 
            'YTD Total Cost':'sum', 'Annualized Total Cost':'sum', 'Benchmark Total Cost':'sum', 'YTD IP Utilization':'sum', 'Annualized IP Utilization':'sum', 'Benchmark IP Utilization':'sum',
            'Baseline Average KCCQ Score':'mean', 'YTD Average KCCQ Score':'mean'}).reset_index()

        df_agg['Patient %'] = df_agg['Pt Count']/995000
        df_agg['YTD Utilization per Thousand'] = 1000 * df_agg['YTD Utilization']/df_agg['Pt Count']
        df_agg['Annualized Utilization per Thousand'] = 1000 * df_agg['Annualized Utilization']/df_agg['Pt Count']
        df_agg['Benchmark Utilization per Thousand'] = 1000 * df_agg['Benchmark Utilization']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Utilization per Thousand'] = (df_agg['Annualized Utilization'] - df_agg['Benchmark Utilization'])/df_agg['Benchmark Utilization']
        df_agg['YTD Total Cost'] = df_agg['YTD Total Cost']/df_agg['Pt Count']
        df_agg['Annualized Total Cost'] = df_agg['Annualized Total Cost']/df_agg['Pt Count']
        df_agg['Benchmark Total Cost'] = df_agg['Benchmark Total Cost']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Total Cost'] = (df_agg['Annualized Total Cost'] - df_agg['Benchmark Total Cost'])/df_agg['Benchmark Total Cost']
        df_agg['YTD Unit Cost'] = df_agg['YTD Total Cost']/df_agg['YTD Utilization']
        df_agg['Annualized Unit Cost'] = 1000 * df_agg['Annualized Total Cost']/df_agg['Annualized Utilization']
        df_agg['Benchmark Unit Cost'] = 1000 * df_agg['Benchmark Total Cost']/df_agg['Benchmark Utilization']
        df_agg['Diff % from Benchmark Unit Cost'] = (df_agg['Annualized Unit Cost'] - df_agg['Benchmark Unit Cost'])/df_agg['Benchmark Unit Cost']
        df_agg['YTD Hospitalization Rate per Thousand'] = 1000 * df_agg['YTD IP Utilization']/df_agg['Pt Count']
        df_agg['Annualized Hospitalization Rate per Thousand'] = 1000 * df_agg['Annualized IP Utilization']/df_agg['Pt Count']
        df_agg['Benchmark Hospitalization Rate per Thousand'] = 1000 * df_agg['Benchmark IP Utilization']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Hospitalization Rate per Thousand'] = (df_agg['Annualized IP Utilization'] - df_agg['Benchmark IP Utilization'])/df_agg['Benchmark IP Utilization']

        df_agg['Baseline Average KCCQ Score'] = df_agg['Baseline Average KCCQ Score']/df_agg['Pt Count']
        df_agg['YTD Average KCCQ Score'] = df_agg['YTD Average KCCQ Score']/df_agg['Pt Count']
        df_agg['KCCQ Improvement from Baseline'] = df_agg['YTD Average KCCQ Score'] - df_agg['Baseline Average KCCQ Score']

        show_column = selected_dimension + ['Patient %'] + m 
        if 'Diff % from Benchmark Total Cost' in m:
            df_agg =  df_agg[show_column].sort_values(by =  'Diff % from Benchmark Total Cost', ascending =False)
        else:
            df_agg = df_agg[show_column]
    else:
        show_column = ['Patient %'] + m 
        df_agg = df_drilldown_filtered[show_column]
    
    
    return [{"name": i, "id": i, "selectable":True,"type":"numeric", "format": FormatTemplate.percentage(1)} if i in percent_list else {"name": i, "id": i, "selectable":True, "type":"numeric","format": FormatTemplate.money(0)} if i in dollar_list else {"name": i, "id": i, "selectable":True, "type":"numeric","format": Format(precision=1, scheme = Scheme.fixed)} for i in show_column], df_agg.to_dict('records')

##### KCCQ callbacks #####

# modify lv1 criteria
@app.callback(
    Output("popover-mod-dim-lv1-kccq","is_open"),
    [Input("button-mod-dim-lv1-kccq","n_clicks"),],
   # Input("mod-button-mod-measure","n_clicks"),
    [State("popover-mod-dim-lv1-kccq", "is_open")],
)
def toggle_popover_mod_criteria(n1, is_open):
    if n1 :
        return not is_open
    return is_open


#update patient lv1 table  and filter1 on following page based on criteria button
@app.callback(
   [ Output("drill_patient_lv1_kccq","children"),
     Output("filter_patient_1_2_name_kccq","children"),
     Output("filter_patient_1_2_contain_kccq",'children'),
     Output("dimname_on_patient_lv1_kccq","children"),
   ],
   [Input("list-dim-lv1-kccq","value")] 
)
def update_table_dimension(dim):
    df=drilldata_process_kccq(df_drilldown,dim)

    return drillgraph_lv1_kccq(df,"dashtable_patient_lv1_kccq",dim),dim,filter_template_crhr(dim,"filter_patient_1_2_value_kccq"),'By '+dim


#update patient filter1 on following page based on selected rows

@app.callback(
    Output("filter_patient_1_2_value_kccq","value"),   
   [ Input("dashtable_patient_lv1_kccq","selected_row_ids"),
   ] 
)
def update_filter1value_patient(row):

    if row is None or row==[]:
        row_1='All'
    else:row_1=row[0]        
    
    return row_1

#update patient data lv2 on filter1

@app.callback(
    Output("dashtable_patient_lv2_kccq","data"),   
   [Input("filter_patient_1_2_value_kccq","value"),], 
   [State("filter_patient_1_2_name_kccq","children"),]
)
def update_filter1value_patient(val,dim):

    df= drilldata_process_kccq(df_drilldown,'Category',dim,val)       
    
    return df.to_dict('records')




## kccq modal
@app.callback(
    Output("drilldown-modal-centered-kccq", "is_open"),
    [Input("drilldown-open-centered-kccq", "n_clicks"), Input("drilldown-close-centered-kccq", "n_clicks")],
    [State("drilldown-modal-centered-kccq", "is_open")],
)
def toggle_modal_dashboard_domain_selection(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    [Output('dimension_filter_1_kccq', 'options'),
    Output('dimension_filter_1_kccq', 'value'),
    Output('dimension_filter_1_kccq', 'multi')],
    [Input('dimension_filter_selection_1_kccq', 'value')]
    )
def filter_dimension_1(v):
    if v:
        if v == 'Service Category':
            return [{"label": 'All', "value": 'All'}]+[{"label": k, "value": k} for k in list(filter_list.keys())], 'All', False
        else:
            return [{"label": k, "value": k} for k in dimension[v]], dimension[v], True
    return [], [], True


@app.callback(
    [Output('dimension_filter_2_kccq', 'options'),
    Output('dimension_filter_2_kccq', 'value'),
    Output('dimension_filter_2_kccq', 'multi')],
    [Input('dimension_filter_selection_1_kccq', 'value'),
    Input('dimension_filter_selection_2_kccq', 'value'),
    Input('dimension_filter_1_kccq', 'value')]
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
    Output('dropdown-dimension-2-kccq','clearable'),
    [Input('dropdown-dimension-3-kccq','value')]
    )
def dropdown_clear(v):
    if v:
        return False
    return True

@app.callback(
    [Output('dropdown-dimension-2-kccq','options'),
    Output('dropdown-dimension-2-kccq','disabled')],
    [Input('dropdown-dimension-1-kccq','value')]
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
    [Output('dropdown-dimension-3-kccq','options'),
    Output('dropdown-dimension-3-kccq','disabled')],
    [Input('dropdown-dimension-1-kccq','value'),
    Input('dropdown-dimension-2-kccq','value')]
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
    [Output('dimension_filter_selection_2_kccq', 'options'),
    Output('dimension_filter_selection_2_kccq', 'disabled')],
    [Input('dimension_filter_selection_1_kccq', 'value'),
    Input('dimension_filter_1_kccq', 'value')]
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
    Output('dropdown-measure-1-kccq', 'options'),
    [Input('dropdown-dimension-1-kccq','value'),
    Input('dropdown-dimension-2-kccq','value'),
    Input('dropdown-dimension-3-kccq','value')]
    )
def update_measures(d1, d2, d3):
    d = [d1, d2, d3]
    measure_kccq = ['YTD Utilization per Thousand', 'Annualized Utilization per Thousand', 'Benchmark Utilization per Thousand', 'Diff % from Benchmark Utilization per Thousand',
        'YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost', 'Diff % from Benchmark Total Cost',
        'YTD Unit Cost', 'Annualized Unit Cost', 'Benchmark Unit Cost', 'Diff % from Benchmark Unit Cost',
        'YTD Hospitalization Rate per Thousand', 'Annualized Hospitalization Rate per Thousand', 'Benchmark Hospitalization Rate per Thousand', 'Diff % from Benchmark Hospitalization Rate per Thousand',
        'Baseline Average KCCQ Score', 'YTD Average KCCQ Score', 'KCCQ Improvement from Baseline']
    if 'KCCQ Category' in d:
        return [{"label": k, "value": k} for k in measure_kccq]
    else:
        return [{"label": k, "value": k} for k in measure]

@app.callback(
    [Output('datatable-tableview-kccq', "columns"),
    Output('datatable-tableview-kccq', "data")],
    [Input('dropdown-dimension-1-kccq','value'),
    Input('dropdown-dimension-2-kccq','value'),
    Input('dropdown-dimension-3-kccq','value'),
    Input('dimension_filter_selection_1_kccq','value'),
    Input('dimension_filter_selection_2_kccq','value'),
    Input('dimension_filter_1_kccq','value'),
    Input('dimension_filter_2_kccq','value'),
    Input('dropdown-measure-1-kccq', 'value')]
    )
def datatable_data_selection(v1, v2, v3, d1, d2, f1, f2, m):
    if d1:
        if d1 == 'Service Category':
            if d2 is None:
                if f1 == 'All':
                    df_drilldown_filtered = df_drilldown_reshape
                    cate_cnt = cate_mix_cnt
                else:
                    df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape['Service Category'].isin([f1])]
                    cate_cnt = len(filter_list[f1])
            elif f1 != 'All' and d2 == 'Sub Category':
                df_drilldown_filtered = df_drilldown_reshape[(df_drilldown_reshape['Service Category'].isin([f1])) & (df_drilldown_reshape['Sub Category'].isin(f2))]
                cate_cnt = len(f2)
            else:
                df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape[d2].isin(f2)]
                if f1 == 'All':
                    cate_cnt = cate_mix_cnt
                else:
                    cate_cnt = len(filter_list[f1])
        elif d2 == 'Service Category':
            if f2 == 'All':
                df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape[d1].isin(f1)]
                cate_cnt = cate_mix_cnt
            else:
                df_drilldown_filtered = df_drilldown_reshape[(df_drilldown_reshape['Service Category'].isin([f2])) & (df_drilldown_reshape[d1].isin(f1))]
                cate_cnt = len(filter_list[f2])
        else:
            if d2:
                df_drilldown_filtered = df_drilldown_reshape[(df_drilldown_reshape[d1].isin(f1)) & (df_drilldown_reshape[d2].isin(f2))]
                cate_cnt = cate_mix_cnt
            else: 
                df_drilldown_filtered = df_drilldown_reshape[df_drilldown_reshape[d1].isin(f1)]
                cate_cnt = cate_mix_cnt
    else:
        df_drilldown_filtered = df_drilldown_reshape
        cate_cnt = cate_mix_cnt

    df_drilldown_filtered['YTD IP Utilization'] = df_drilldown_filtered.apply(lambda x: x['YTD Utilization'] if x['Service Category'] == 'Inpatient' else 0, axis = 1)
    df_drilldown_filtered['Annualized IP Utilization'] = df_drilldown_filtered.apply(lambda x: x['Annualized Utilization'] if x['Service Category'] == 'Inpatient' else 0, axis = 1)
    df_drilldown_filtered['Benchmark IP Utilization'] = df_drilldown_filtered.apply(lambda x: x['Benchmark Utilization'] if x['Service Category'] == 'Inpatient' else 0, axis = 1)

    table_column = []
    selected_dimension = []
    if v1 is not None:
        selected_dimension.append(v1)
    if v2 is not None:
        selected_dimension.append(v2)
    if v3 is not None:
        selected_dimension.append(v3)

    table_column.extend(list(set(selected_dimension + ['Service Category', 'Sub Category', 'KCCQ Category'])))
    table_column.append("Pt Count")
    percent_list = ['Diff % from Benchmark Utilization per Thousand', 'Diff % from Benchmark Total Cost', 'Diff % from Benchmark Unit Cost', 'Patient %', 'Diff % from Benchmark Hospitalization Rate per Thousand']
    dollar_list = ['YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost', 'YTD Unit Cost', 'Annualized Unit Cost', 'Benchmark Unit Cost']
    if len(selected_dimension) > 0:

        table_column.extend(measure_ori) 
        df_agg_pre = df_drilldown_filtered[table_column].groupby(by = list(set(selected_dimension + ['Service Category', 'Sub Category', 'KCCQ Category']))).sum().reset_index()
        df_agg = df_agg_pre[table_column].groupby(by = selected_dimension).agg({'Pt Count':'mean', 'YTD Utilization':'sum', 'Annualized Utilization':'sum', 'Benchmark Utilization':'sum', 
            'YTD Total Cost':'sum', 'Annualized Total Cost':'sum', 'Benchmark Total Cost':'sum', 'YTD IP Utilization':'sum', 'Annualized IP Utilization':'sum', 'Benchmark IP Utilization':'sum',
            'Baseline Average KCCQ Score':'mean', 'YTD Average KCCQ Score':'mean'}).reset_index()

        df_agg['Patient %'] = df_agg['Pt Count']/995000
        df_agg['YTD Utilization per Thousand'] = 1000 * df_agg['YTD Utilization']/df_agg['Pt Count']
        df_agg['Annualized Utilization per Thousand'] = 1000 * df_agg['Annualized Utilization']/df_agg['Pt Count']
        df_agg['Benchmark Utilization per Thousand'] = 1000 * df_agg['Benchmark Utilization']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Utilization per Thousand'] = (df_agg['Annualized Utilization'] - df_agg['Benchmark Utilization'])/df_agg['Benchmark Utilization']
        df_agg['YTD Total Cost'] = df_agg['YTD Total Cost']/df_agg['Pt Count']
        df_agg['Annualized Total Cost'] = df_agg['Annualized Total Cost']/df_agg['Pt Count']
        df_agg['Benchmark Total Cost'] = df_agg['Benchmark Total Cost']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Total Cost'] = (df_agg['Annualized Total Cost'] - df_agg['Benchmark Total Cost'])/df_agg['Benchmark Total Cost']
        df_agg['YTD Unit Cost'] = df_agg['YTD Total Cost']/df_agg['YTD Utilization']
        df_agg['Annualized Unit Cost'] = 1000 * df_agg['Annualized Total Cost']/df_agg['Annualized Utilization']
        df_agg['Benchmark Unit Cost'] = 1000 * df_agg['Benchmark Total Cost']/df_agg['Benchmark Utilization']
        df_agg['Diff % from Benchmark Unit Cost'] = (df_agg['Annualized Unit Cost'] - df_agg['Benchmark Unit Cost'])/df_agg['Benchmark Unit Cost']
        df_agg['YTD Hospitalization Rate per Thousand'] = 1000 * df_agg['YTD IP Utilization']/df_agg['Pt Count']
        df_agg['Annualized Hospitalization Rate per Thousand'] = 1000 * df_agg['Annualized IP Utilization']/df_agg['Pt Count']
        df_agg['Benchmark Hospitalization Rate per Thousand'] = 1000 * df_agg['Benchmark IP Utilization']/df_agg['Pt Count']
        df_agg['Diff % from Benchmark Hospitalization Rate per Thousand'] = (df_agg['Annualized IP Utilization'] - df_agg['Benchmark IP Utilization'])/df_agg['Benchmark IP Utilization']

        df_agg['Baseline Average KCCQ Score'] = df_agg['Baseline Average KCCQ Score']/df_agg['Pt Count']
        df_agg['YTD Average KCCQ Score'] = df_agg['YTD Average KCCQ Score']/df_agg['Pt Count']
        df_agg['KCCQ Improvement from Baseline'] = df_agg['YTD Average KCCQ Score'] - df_agg['Baseline Average KCCQ Score']

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
    app.run_server(host="127.0.0.1",debug=True, port = 8052)









