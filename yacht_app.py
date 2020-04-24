from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route("/")
def home():
	return render_template("index.html")

@app.route('/results')
def results():
	data = []
	with open("output/boatlist.json", "r") as jdata:
		data = json.load(jdata)
	return render_template("results.html", boatlist=data['boats'],predata=data['fileinfo'])

@app.route("/", methods=['POST'])
def echo():
	#get index form data
	if request.method == "POST":
		inputcurr=request.form["inputcurr"]
		minprice=request.form["minprice"]
		maxprice=request.form["maxprice"]
		minlength=request.form["minlength"]
		maxlength=request.form["maxlength"]
		texta= minlength + "–" + maxlength +"ft\n" + inputcurr +": $" +minprice + "-" + maxprice
		textb= minlength + "–" + maxlength +"ft<br/>" + inputcurr +": $" +minprice + "-" + maxprice
		# build sort param ie data['boats'].sort(key=lambda s: s['Location'])
		sortparam=request.form["inputsearch"]
		if sortparam == 'Location':
			keyparam = lambda s: s['Location']
		elif sortparam == 'Price':
			#keyparam = lambda s: float('inf') if s['Price'].lower() == "call for price" else int(s['Price'].replace(',', ''))
			keyparam = lambda s: int(s['Price'].replace(',', '')) if s['Price'].replace(',', '').replace('-', '').isdigit() else float('inf')
		elif sortparam == 'Size':
			keyparam = lambda s: s['Size']

		# import various libraries
		import requests
		from bs4 import BeautifulSoup
		import re
		#enable math.ceil
		import math
		# enable sys.exit()
		import sys
		import csv
		import json
		from datetime import datetime
		import os

		# set header to avoid being labeled a bot
		headers = {
			'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
		}

		# set base url
		baseurl='https://www.yachtworld.com/boats-for-sale/type-sail/region-northamerica/'

		# input low number
		if minprice == '':
			minpricenum = '30000'
		else:
			minpricenum = minprice
		print(minpricenum)

		# input high number
		if maxprice == '':
			maxpricenum = '120000'
		else:
			maxpricenum = maxprice
		print(maxpricenum)

		# input currency
		if inputcurr == '':
			curr = 'CAD'
		else:
			curr = inputcurr
		print(curr)

		# input low length
		if minlength == '':
			lowlen = '34'
		else:
			lowlen = minlength
		print(lowlen)

		# input high length
		if maxlength == '':
			highlen = '48'
		else:
			highlen = maxlength
		print(highlen)

		# set variables
		pricerange = '&price=' + minpricenum + '-' + maxpricenum
		currlen = '?currency=' + curr + '&length=' + lowlen + '-' + highlen

		# set regions
		wash = 'country-united-states/state-washington/'
		oreg = 'country-united-states/state-oregon/'
		bc = 'country-canada/province-british-columbia/'

		# create list of region url variables
		urllist=[bc,wash,oreg]

		# set path to export as file
		dirname = os.path.dirname(__file__)
		path_folder = os.path.join(dirname, "output/")
		print (path_folder)

		# set date and time
		now = datetime.now()
		dt_string = now.strftime("%B %d, %Y %H:%M")

		# create empty list
		arrayjson = []

		#loop though pages in urllist
		for page in urllist:
		# get url
			urlpath = baseurl+page+currlen+pricerange
			page = requests.get(urlpath, timeout=5)

			boatpg = BeautifulSoup(page.content, "html.parser")

			# find errors by comparing requested url from listed url
			alert = page
			if page.url != urlpath:
				continue

			# find boat listings section
			boatlist = boatpg.find('div', class_="search-right-col")

			#find single boat listing
			boatlisting = boatlist.find_all('a')

			#loop though listing and append to list
			for listname in boatlisting:
				nameurl = listname['href']
				thumb = listname.find("meta",  property="image")
				#add https and find content of meta and substring url to remove first two characters
				thumburl="https://" + thumb["content"][2:]
				name = listname.find('div', property="name")
				priceraw = listname.find('div', class_="price")
				if priceraw.text != "Call for Price":
					#remove extra info from front and back
					price = re.search("\$.*? (?= *)",priceraw.text)
					cost = price.group()[1:-1]
				else:
					cost="Call for Price"
				sizeyear = listname.find('div', class_="listing-card-length-year")
				location = listname.find('div', class_="listing-card-location")
				#write to json format
				writejson =  {
						"URL": nameurl,
						"Name": name.text,
						"Price": cost,
						"Size": sizeyear.text,
						"Location":location.text,
						"Thumb": thumburl
					}
				# append to list
				arrayjson.append(writejson)

		#add Preface list (array)
		arraypreface = []

		preface = {
					'Date': dt_string,
					'Text': 'Results are a Yachtworld search of sailboats in Washington, Oregon and B.C.',
					'Currency': curr,
					'Low': minpricenum,
					'High': maxpricenum,
					'Short':lowlen,
					'Long': highlen,
					'Creator': 'http://neverforever.ca'
			}
		#append to list
		arraypreface.append(preface)

		# open json file with path
		with open(path_folder+'boatlist.json', 'w') as outfile:
			#dump two lists with dict names and add formatting (default=str solves date issue)
			json.dump({'fileinfo': arraypreface, 'boats': arrayjson}, outfile, indent=4, default=str)
	data = []
	with open(path_folder+"boatlist.json", "r") as jdata:
		data = json.load(jdata)
		data['boats'].sort(key=keyparam)
	return render_template('results.html', boatlist=data['boats'],predata=data['fileinfo'])


