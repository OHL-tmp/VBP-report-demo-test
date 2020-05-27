#!/usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table

import pandas as pd
import numpy as np

import urllib.parse as url_parse
import flask 
from io import StringIO, BytesIO

from app import app
import contract_manager
import contract_manager_drilldown
import contract_optimizer
import contract_report_generator
import contract_measures_library

df_test=pd.read_excel("downloads/test.xlsx", index_col = 0)


def launch_layout():
    return html.Div([

                    html.Div(
                        [
                            
                            html.Video(src=app.get_asset_url("launch_mesh.mov"), autoPlay=True, loop=True, style={"height":"45rem","border-bottom":"none", "text-align":"center"})
                        ],
                        style={"text-align":"center"}
                    ),
                    html.Div(
                        [
                            html.P("© 2020 Sinolation. ")
                        ],
                        style={"text-align":"center", "font-size":"0.6rem"}
                    ),
                    html.Div(
                        [
                            html.H1(u"ValueGen Solution",style={"background-color":"transparent","font-size":"5rem"}),
                            dbc.Card([
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(dbc.Button("Contract Optimizer", color="light", className="mr-1", href = "/vbc-demo/contract-optimizer/", style={"font-family":"NotoSans-Regular", "font-size":"1rem", "padding":"1rem","border-radius":"1rem","border":"1px solid #ececf6","box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.1), 0 6px 20px 0 rgba(0, 0, 0, 0.1)"}), style={"border-radius":"1rem","width":"5rem"}),
                                                dbc.Col(dbc.Button("Contract Manager", color="light", className="mr-1", href = "/vbc-demo/contract-manager/", style={"font-family":"NotoSans-Regular", "font-size":"1rem", "padding":"1rem", "padding":"1rem", "border-radius":"1rem","border":"1px solid #ececf6","box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.1), 0 6px 20px 0 rgba(0, 0, 0, 0.1)"}), style={"border-radius":"1rem","width":"5rem"}),
                                                dbc.Col(dbc.Button("Tele Case Manager", color="light", className="mr-1", href = "/vbc-demo/tele-case-manager/", style={"font-family":"NotoSans-Regular", "font-size":"1rem", "padding":"1rem", "border-radius":"1rem","border":"1px solid #ececf6","box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.1), 0 6px 20px 0 rgba(0, 0, 0, 0.1)"}), style={"border-radius":"1rem","width":"5rem"}),
                                            ],
                                            style={"background-color":"none", "font-family":"NotoSans-Regular", "font-size":"1rem", "border":"none","padding-top":"1rem","padding-bottom":"1rem","padding-left":"20rem","padding-right":"20rem"}
                                        )
                                    ]
                                )

                            ],
                            style={"background-color":"transparent", "border":"none"}
                            ),
                        ],
                        style={"margin-top":"-30rem","background-color":"transparent","text-align":"center"}
                    )
                    
                ],
                style={"background-color":"#fff","height":"100vh"})



# Describe the layout/ UI of the app
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)


# Update page
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/vbc-demo/contract-manager/":
        return contract_manager.layout
    elif pathname == "/vbc-demo/contract-manager-drilldown/":
        return contract_manager_drilldown.layout
    elif pathname == "/vbc-demo/contract-optimizer/":
        return contract_optimizer.layout
    elif pathname == "/vbc-demo/contract-optimizer/measures-library/":
        return contract_measures_library.layout
    elif pathname == "/vbc-demo/contract-manager/report-generator/":
        return contract_report_generator.layout
    else:
        return launch_layout()

#####################################3
     


@app.server.route('/downloads/<filename>', methods = ['GET'])
def serve_static(filename):

    filename = 'downloads/' + filename
    return flask.send_file(filename, as_attachment=True)




if __name__ == "__main__":
    app.run_server(host='0.0.0.0',port = 8098)
                        