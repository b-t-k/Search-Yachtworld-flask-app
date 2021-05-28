from flask import request, jsonify, render_template, send_from_directory, flash, redirect, url_for
import json
import os
# import app from __init__
from search_boatlisting import app
from search_boatlisting.forms import boatsearchform, loginform
from search_boatlisting.loops import *
from search_boatlisting.classes import *

#set defaults for search
minprice_d='50000'
maxprice_d='100000'
minlength_d='34'
maxlength_d='48'

#routes are where flask goes to look for files
@app.route("/")
def home():	
	form = boatsearchform()
	return render_template("index.html", form = form, minprice = minprice_d, maxprice=maxprice_d,minlength=minlength_d,maxlength=maxlength_d)

@app.route('/results')
def results():
	data = []
	with open("search_boatlisting/output/boatlist.json", "r") as jdata:
		data = json.load(jdata)
	return render_template("results.html", boatlist=data['boats'],predata=data['fileinfo'], title='Sailboat Search Results')

@app.route('/output/<path:filename>', methods=['GET'])
def download(filename):
	return send_from_directory(os.path.join(app.root_path, 'output'), filename)

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Main Search routine using home page
@app.route("/", methods=['GET', 'POST'])
def echo():
	#get index form data
	form = boatsearchform()

	if request.method == "POST":
			
		# !! sitename using wtforms
		sitename=(form.sitename.data)
		# !! siteneame using requests
		#sitename=request.form["sitename"]
		# print('ECHO SITENAME: ')
		# print(sitename)
		inputcurr=request.form["inputcurr"]
		# print(inputcurr)
		minprice=request.form["minprice"]
		maxprice=request.form["maxprice"]
		minlength=request.form["minlength"]
		maxlength=request.form["maxlength"]
		sortparam=request.form["inputsearch"]
		if sortparam == 'Location':
			keyparam = lambda s: s['Location']
		elif sortparam == 'Price':
			#keyparam = lambda s: float('inf') if s['Price'].lower() == "call for price" else int(s['Price'].replace(',', ''))
			keyparam = lambda s: int(s['Price'].replace(',', '')) if s['Price'].replace(',', '').replace('-', '').isdigit() else float('inf')
		elif sortparam == 'Size':
			keyparam = lambda s: s['Size']

	## SET DEFAULTS
		# input low length
		if minlength == '':
			minlength = minlength_d
		else:
			minlength = minlength

		# input high length
		if maxlength == '':
			maxlength = maxlength_d
		else:
			maxlength = maxlength
		#print(maxlength)


		#set low price
		if minprice == '':
			minprice = minprice_d
		else:
			minprice = minprice
		#print(echo.minpricenum)

		#set high price
		if maxprice == '':
			maxprice = maxprice_d
		else:
			maxprice = maxprice

		# set header to avoid being labeled a bot
		headers = {
			'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
		}

		# set class object with form input
		searchparameters = boatsearchinput(sitename, inputcurr, minprice, maxprice, minlength, maxlength, sortparam)
		
		# import various libraries
		import csv
		import json
		import os
		# # import requests
		# # from bs4 import BeautifulSoup
		# # import re
		# # import math
		# # from datetime import datetime

	# Start Process
		# set path to export as file
		dirname = os.path.dirname(__file__)
		path_folder = os.path.join(dirname, "search_boatlisting/output/")
		#print (path_folder)

		# set date and time
		now = datetime.now()
		dt_string = now.strftime("%B %d, %Y %H:%M")

		# create empty list
		arrayjson = []
		urljson =[]

	#CALL THE TWO FUNCTIONS!!!!!
		if sitename == "SBL":
			# return two variables from function
			listsite, boatcount = sailboatlisting_loop(searchparameters,urljson,arrayjson)
		elif sitename == "YW":
			listsite, boatcount = yachtworld_loop(searchparameters,urljson,arrayjson)
		elif sitename == "both":
			listsite, boatcountSBL = sailboatlisting_loop(searchparameters,urljson,arrayjson)
			listsite, boatcountYW = yachtworld_loop(searchparameters,urljson,arrayjson)
			listsite = 'Yachtworld & Sailboatlisting'
			boatcount = boatcountSBL + boatcountYW

	# Add Preface list (array)
		arraypreface = []

		preface = {
					'Date': dt_string,
					'urllisting': urljson,
					'Text': 'Results are a search of sailboats in Washington, Oregon and B.C. from ',
					"Listing": listsite,
					'Boatcount': boatcount,
					'Currency': inputcurr,
					'Low': minprice,
					'High': maxprice,
					'Short':minlength,
					'Long': maxlength,
					'Creator': 'http://neverforever.ca'
			}
		#append to list
		arraypreface.append(preface)

		# open json file with path
		with open('search_boatlisting/output/boatlist.json', 'w') as outfile:
			#dump two lists with dict names and add formatting (default=str solves date issue)
			json.dump({'fileinfo': arraypreface, 'boats': arrayjson}, outfile, indent=4, default=str)

	# write to excel
	import tablib

	datax = tablib.Dataset()
	datax.append_separator(dt_string + ' Currency=' + inputcurr)
	datax.json = json.dumps(arrayjson)

	data_export = datax.export('xlsx')
	with open('search_boatlisting/output/boatlist.xlsx', 'wb') as f:  # open the xlsx file
		f.write(data_export)  # write the dataset to the xlsx file
	f.close()


	data = []
	with open("search_boatlisting/output/boatlist.json", "r") as jdata:
		data = json.load(jdata)
		data['boats'].sort(key=keyparam)
	return render_template('results.html', boatlist=data['boats'],predata=data['fileinfo'])