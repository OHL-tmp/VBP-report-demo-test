import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash_table.FormatTemplate as FormatTemplate

import pandas as pd
import numpy as np

import pathlib
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Scheme



'''app = dash.Dash(__name__, url_base_pathname='/vbc-demo/dashboard/')

server = app.server'''

#df_drilldown = pd.read_csv("data/drilldown_sample_5.csv")
#df_drilldown["Diff % from Target Utilization"] = df_drilldown.apply(lambda x: format( x['Annualized Utilization'] - x['Target Utilization']/x['Target Utilization'], '.2%'), axis = 1)
#df_drilldown['Diff % from Target Total Cost'] = df_drilldown.apply(lambda x: format( x['Annualized Total Cost'] - x['Target Total Cost']/x['Target Total Cost'], '.2%'), axis = 1)
#df_drilldown['YTD Unit Cost'] = df_drilldown.apply(lambda x: round( x['YTD Total Cost']/x['YTD Utilization'], 2), axis = 1)
#df_drilldown['Annualized Unit Cost'] = df_drilldown.apply(lambda x: round( x['Annualized Total Cost']/x['Annualized Utilization'], 2), axis = 1)
#df_drilldown['Target Unit Cost'] = df_drilldown.apply(lambda x: round( x['Target Total Cost']/x['Target Utilization'], 2), axis = 1)
#df_drilldown['Diff % from Target Unit Cost'] = df_drilldown.apply(lambda x: format( x['Annualized Unit Cost'] - x['Target Unit Cost']/x['Target Unit Cost'], '.2%'), axis = 1)

dimension = {'Age Band' : ['<65', '65-74', '75-85', '>=85'], 'Gender' : ['F', 'M'], 
'Patient Health Risk Level' : ['Low', 'Mid', 'High'], 'NYHA Class' : ['I', 'II', 'III', 'IV'], 
       'Medication Adherence' : ['Compliant', 'Non-compliant'], 'Managing Physician (Group)': ['Group A', 'Group B', 'Group C', 'Group D'], 
       'Weight Band' : [], 'Comorbidity Type' : [], 'Comorbidity Score' : [], 'Ejection Fraction' : [], 'Years Since HF Diagnosis' : [], 'Prior Use of ACE/ARB' : []}
measure = ['YTD Utilization per Thousand', 'Annualized Utilization per Thousand', 'Benchmark Utilization per Thousand', 'Diff % from Benchmark Utilization per Thousand',
		'YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost', 'Diff % from Benchmark Total Cost',
		'YTD Unit Cost', 'Annualized Unit Cost', 'Benchmark Unit Cost', 'Diff % from Benchmark Unit Cost',
		'YTD Hospitalization Rate per Thousand', 'Annualized Hospitalization Rate per Thousand', 'Benchmark Hospitalization Rate per Thousand', 'Diff % from Benchmark Hospitalization Rate per Thousand']
measure_ori = ['YTD Utilization', 'Annualized Utilization', 'Benchmark Utilization', 
		'YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost',
		'YTD IP Utilization', 'Annualized IP Utilization', 'Benchmark IP Utilization']
filter_list = {
       'Inpatient' : ['Acute myocardial infarction', 'CABG', 'Cardiac Arrhythmia', 'Cardiac arrest and ventricular fibrillation', 'Heart Failure', 'Hypertension', 'ICD', 'Others', 'PCI', 'Pacemaker Implant', 'Pleural effusion', 'Renal Failure'],
 		'Outpatient ER' : ['AMI', 'Aftercare following surgery', 'COPD', 'Cardiac dysrhythmias', 'Diabetes', 'Heart Failure', 'Hypertension', 'Others', 'Respiratory system and chest symptoms'], 
 		'Outpatient Others (Non ER)' : ['Ambulance', 'Durable Medical Equipment (DME)', 'Lab/Pathology', 'Observation', 'Others', 'Outpatient Surgery', 'Radiology'], 
 		'Professional Services' : [ 'Administered Drugs', 'Anesthesia', 'Lab/Pathology', 'Office Visits', 'Others', 'Radiology', 'Surgical'], 
 		'Drug Others (Excl. Entrestro)' : ['ACE /ARB', 'Aldosterone receptor antagonists', 'Beta Blocker', 'Diuretics', 'Others', 'Vasodilators'], 
 		'Drug Entresto': ['Entresto'], 'Home Health' : ['Home Health'], 'Skilled Nursing Facility' : ['Skilled Nursing Facility'], 'Hospice' : ['Hospice']}

cate_mix_cnt = 0
for k in list(filter_list.keys()):
	cate_mix_cnt = cate_mix_cnt + len(filter_list[k])


def tableview():
	return html.Div(
		[
			dbc.Row(
				[
					dbc.Col(
						[
							html.Div(
								[
									html.H4("Select Dimension", style={"font-size":"1rem","padding-left":"0.5rem", "padding-top":"0.5rem"}),
									html.H5("First Dimension", style={"font-size":"0.8rem","color":"#919191","padding-left":"0.5rem", "padding-top":"0.5rem"}),
									dcc.Dropdown(
										id = "dropdown-dimension-1-crhr",
										placeholder ="...",
										options = [{"label": 'Service Category', "value": 'Service Category'}, {"label": 'Sub Category', "value": 'Sub Category', 'disabled': True}] 
										+ [{"label": k, "value": k, 'disabled' : True} if len(dimension[k]) == 0 else {"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys())],
										value = 'Patient Health Risk Level',
										clearable = False,
										style = {"font-family":"NotoSans-Condensed","font-size":"0.8rem"}
										),
									html.H5("Second Dimension", style={"font-size":"0.8rem","color":"#919191","padding-left":"0.5rem", "padding-top":"0.5rem"}),
									dcc.Dropdown(
										id = "dropdown-dimension-2-crhr",
										disabled=True,
										placeholder ="...",
										style = {"font-family":"NotoSans-Condensed","font-size":"0.8rem"}
										),
									html.H5("Third Dimension", style={"font-size":"0.8rem","color":"#919191","padding-left":"0.5rem", "padding-top":"0.5rem"}),
									dcc.Dropdown(
										id = "dropdown-dimension-3-crhr",
										disabled=True,
										placeholder ="...",
										style = {"font-family":"NotoSans-Condensed","font-size":"0.8rem"}
										),
									html.H4("Select Measures", style={"font-size":"1rem","padding-left":"0.5rem", "padding-top":"1rem"}),
									dcc.Dropdown(
										id = "dropdown-measure-1-crhr",
										options = [{"label": k, "value": k} for k in measure],
										value = ['Diff % from Benchmark Total Cost', 'YTD Total Cost', 'Annualized Total Cost', 'Benchmark Total Cost'],
										placeholder ="Select measures",
										multi = True,
										style = {"font-family":"NotoSans-Condensed","font-size":"0.8rem"}
										),
								]
							),
							html.Hr(className="ml-1"),
							html.Div(
								[
									html.H4("Filters", style={"font-size":"1rem","padding-left":"0.5rem", "padding-top":"0.5rem"}),
									html.H5("Filter 1", style={"font-size":"0.8rem","color":"#919191","padding-left":"0.5rem", "padding-top":"0.5rem"}),
									dcc.Dropdown(
										id = "dimension_filter_selection_1_crhr",
										options = [{"label": 'Service Category', "value": 'Service Category'}, {"label": 'Sub Category', "value": 'Sub Category', 'disabled': True}] 
										+ [{"label": k, "value": k, 'disabled' : True} if len(dimension[k]) == 0 else {"label": k, "value": k, 'disabled' : False} for k in list(dimension.keys())],
										placeholder = "Add a Filter",
										style = {"font-family":"NotoSans-Condensed","font-size":"0.8rem"}
										),
									html.H5("", style={"font-size":"0.8rem"}),
									dcc.Dropdown(
										id = "dimension_filter_1_crhr",
										placeholder = "Select Filter Value",
										multi = True,
										style = {"font-family":"NotoSans-Condensed","font-size":"0.8rem"},
										),
									html.H5("Filter 2", style={"font-size":"0.8rem","color":"#919191","padding-left":"0.5rem", "padding-top":"0.5rem"}),
									dcc.Dropdown(
										id = "dimension_filter_selection_2_crhr",
										options = [{"label": k, "value": k} for k in list(dimension.keys())],
										placeholder = "Add a Filter",
										style = {"font-family":"NotoSans-Condensed","font-size":"0.8rem"}
										),
									html.H5("", style={"font-size":"0.8rem"}),
									dcc.Dropdown(
										id = "dimension_filter_2_crhr",
										placeholder = "Select Filter Value",
										multi = True,
										style = {"font-family":"NotoSans-Condensed","font-size":"0.8rem"}
										),
									html.H5("+ Add more Filter", style={"font-size":"1rem","color":"#1357DD","padding-left":"0.5rem", "padding-top":"0.5rem"}),
								]
							)
						],
						width=3,
						style={"overflow-y":"scroll"}
					),
						
					dbc.Col(
						[
							html.Div(
								[
									html.P("*Default sorted by Diff % from Benchmark Total Cost", style={"font-size":"0.6rem"}),
									dash_table.DataTable(
										id = 'datatable-tableview-crhr',
										style_header = {'height': 'auto', 'width':'auto','whiteSpace':'normal','font-family':'NotoSans-Condensed','font-size':'auto','backgroundColor': '#dce7fc','color':'#1357DD'},
										style_cell = {'font-family':'NotoSans-Regular','font-size':'0.8rem','textAlign': 'center'},
										#fixed_rows={ 'headers': True, 'data': 0 },
										style_table = {'textAlign': 'center'},
										sort_action='native',
										page_size=200,
										style_data_conditional=[
									        {
									            'if': {'row_index': 'odd'},
									            'backgroundColor': 'rgb(248, 248, 248)'
									        }],
										)
								],
								style={"padding-left":"1rem","padding-right":"1rem","padding-bottom":"1rem","overflow":"scroll",'max-height':'60rem'}
							)
							
						],
						width = 9,
						
					),
				]
			)
		]
	)

# app.layout = tableview()

'''
if __name__ == "__main__":
    app.run_server(host="127.0.0.1",debug=True, port=8051)'''