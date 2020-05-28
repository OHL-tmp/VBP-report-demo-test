#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 14:10:52 2020

@author: yanchen
"""
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

from drilldown_tableview import *


# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("Data").resolve()


def modal_drilldown_tableview():
    return html.Div(
                [
                    dbc.Button("OPEN TABLE VIEW", id="drilldown-open-centered", color="light", block=True, style={"color":"#1357DD","border":"1.8px dotted","border-radius":"0.5rem","font-family":"NotoSans-CondensedBlack"}),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(
                                html.Div(
                                    [
                                        html.H2("TABLE VIEW", style={"font-size":"2rem", "color":"#1357DD"})
                                    ],
                                    style={"color":"#1357DD"}
                                )
                            ),
                            dbc.ModalBody(
                                tableview()
                            ),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "CLOSE", id="drilldown-close-centered", className="ml-auto",
                                    style={"margin-right":"20px", "background-color":"#38160f", "border":"none", "border-radius":"10rem", "font-family":"NotoSans-Black", "font-size":"1rem"}
                                )
                            ),
                        ],
                        id="drilldown-modal-centered",
                        size='xl',
                        scrollable=False,
                        backdrop = 'static',
                    ),
                ]
            )




