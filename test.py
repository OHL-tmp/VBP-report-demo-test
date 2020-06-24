import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html
import dash_bootstrap_components as dbc
import dash_table

import base64
import datetime
import io

import os

import pandas as pd
import numpy as np
import json

import flask
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename


app = dash.Dash(__name__, url_base_pathname='/vbc-demo/launch/')

#app.config['UPLOAD_FOLDER'] = '/uploads'

server = app.server

def create_layout(app):
	return html.Div([
			html.H6('choose file to upload'),
			dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
			<form action="/uploader" method="POST" enctype="multipart/form-data">

				<div class="form-group">
				  <label>Select File</label>
				  <div class="custom-file">
					<input type="file" name="file" >
				  </div>
				</div>

				<button type="submit" class="btn btn-primary">Submit</button>

			</form>
			'''),
		])


app.layout = create_layout(app)


# @app.server.route('/upload')
# def upload_file():
#    return render_template('upload.html')
	
@app.server.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		f = request.files['file']
		filename = secure_filename(f.filename)
		
		f.save('C:\\Users\\wangsunyechu\\Documents\\VBP-report-demo-test-REALTIME\\uploads\\'+filename)
		print(request.url)
		return redirect(flask.url_for('/vbc-demo/launch/'))


if __name__ == "__main__":
	app.run_server(host="127.0.0.1", debug = True, port = 8052)