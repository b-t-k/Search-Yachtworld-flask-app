from flask import request, jsonify, render_template, send_from_directory, flash, redirect, url_for
import json
import os
# import app from __init__
from search_boatlisting import app
from search_boatlisting.forms import boatsearchform, loginform
# from .loops import *

#routes are where flask goes to look for files
@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def home():
	form = boatsearchform()
	return render_template("index.html", form = form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	form = loginform()
	if form.validate_on_submit():
		flash(f'Login Approved for {form.email.data}', 'success')
		return redirect(url_for('home'))
	return render_template('login.html', title='Log In', form = form)

@app.route('/results')
def results():
	data = []
	with open("search_boatlisting/output/boatlist.json", "r") as jdata:
		data = json.load(jdata)
	return render_template("results.html", boatlist=data['boats'],predata=data['fileinfo'], title='Sailboat Search Results')

@app.route('/output/<path:filename>', methods=['GET'])
def download(filename):
	return send_from_directory(os.path.join(app.root_path, '/search_boatlisting/output'),filename=filename)

@app.route("/", methods=['GET', 'POST'])
def echo():
	#get index form data
	form = boatsearchform()

	if request.method == "POST":
			
		# !! sitename using wtforms
		sitename=(form.sitename.data)
		# !! siteneame using requests
		#sitename=request.form["sitename"]
		print('ECHO SITENAME: ')
		print(sitename)
		inputcurr=request.form["inputcurr"]
		print(inputcurr)
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
		import csv
		import json
		from datetime import datetime
		import os

		# input currency
		curr = inputcurr
		#print(curr)

		#set Exchange Rate
		exchange = 1.4

		# input low length
		if minlength == '':
			lowlen = '34'
		else:
			lowlen = minlength
		#print(lowlen)

		# input high length
		if maxlength == '':
			highlen = '48'
		else:
			highlen = maxlength
		#print(highlen)

		# set header to avoid being labeled a bot
		headers = {
			'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
		}

		#start sailboatlisting_loop
		def sailboatlisting_loop(maxprice):

			echo.boatcount = 0

			# set base url &  list site
			baseurl='https://www.sailboatlistings.com/cgi-bin/saildata/db.cgi?db=default&uid=default&websearch=1&view_records=1&sb=date&so=descend'
			echo.listsite = 'Sailboatlisting.com'

			#set low number
			echo.minpricenum ='0'

			#set high price
			if maxprice == '':
				echo.maxpricenum = '120000'
				maxprice = echo.maxpricenum
			else:
				echo.maxpricenum = maxprice

			if curr == "CAD":
				echo.maxpricenum = int(echo.maxpricenum) / exchange
				echo.maxpricenum = str(math.trunc(echo.maxpricenum))

			pricerange = '&price-lt=' + echo.maxpricenum
			boatlength = '&length-gt=' + lowlen + '&length-lt=' + highlen

			# create list of url variables
			bc = '&city=bc'
			van = '&city=vancouver'
			british = '&city=british%20columbia'
			wash = '&state=Washington'
			oreg = '&state=Oregon'

			# create list of region url variables
			urllist=[bc,van,british,wash,oreg]


			#loop though pages in urllist
			for page in urllist:
				#set urlpath
				urlpath = baseurl+boatlength+pricerange+page
				print(urlpath)
				urljson.append(urlpath)

				page = requests.get(urlpath, timeout=5)
				boatpg = BeautifulSoup(page.content, "html.parser")

				# find errors by comparing requested url from listed url
				alert = page
				if page.url != urlpath:
					continue

				# find string with item count in Sailboatlisting
				pagecountpattern = re.search('(?<=Your search returned )(\d{1,3}) matches.',boatpg.text)
				#print(pagecountpattern.group(1))

				# set the item count
				totalitemcount = int(pagecountpattern.group(1))

				# set page count
				if totalitemcount > 57:
					pagecount = math.ceil(totalitemcount/57)
				else:
					pagecount = 1

				# set first page
				pagenum = 1

				#Loop Pages
				while pagecount >= pagenum:

					#set current page
					currpagehtml = urlpath+'&nh=' + str(pagenum)
					page = requests.get(currpagehtml, timeout=5)
					boatpg = BeautifulSoup(page.content, "html.parser")
					#print (currpagehtml)

					boatlist = boatpg.find_all('table', attrs={'width':'728'})

					#loop though listing and append to list
					for listname in boatlist:
						thumbimg = listname.find('img')
						if thumbimg is None:
							thumb=""
							print("no image")
						else:
							thumb=thumbimg['src']
							print(thumb)

						nameurllink=listname.find('a')
						nameurl = nameurllink['href']

						#add https
						thumburl="https://www.sailboatlistings.com" + thumb
						#print(thumburl)
						name = listname.find('span', class_="sailheader")

						#find postdate
						postdate=listname.find('span', class_="details")
						postdate = re.search('\d{2}-[a-zA-Z]{3}-\d{4}',postdate.text)
						postdate = postdate.group()
						#print(postdate)
						#Convert to python date
						datedate = datetime.strptime(postdate,'%d-%b-%Y').date()
						#print(datedate)

						#set best before date
						bestbefore = datetime(2018, 1, 1).date()
						if datedate < bestbefore:
							continue

						datedate = datedate.strftime('%d-%b-%Y')

						#find table above td with span that contains details
						table=listname.find('span', class_="sailvb").parent.parent.parent

						#loop though details table to find details
						for i,details in enumerate(table.find_all('span')):
							if i == 1:
								size = details.text
							elif i == 7:
								year = details.text
							elif i == 15:
								location = details.text
							elif i == 17:
								priceraw = details.text

						#remove $ and comma
						price = int(priceraw.strip('$').replace(",", ""))
						if curr == 'CAD':
							#convert to CAD
							price = math.trunc(int(price) * exchange)
						cost = str(price)
						sizeyear = size + " / " + year

						#write to json format
						writejson =  {
								"Name": name.text,
								"Price": cost,
								"Size": sizeyear,
								"Location":location,
								"URL": nameurl,
								"Thumb": thumburl,
								"Listing": echo.listsite,
								"Listdate": datedate
							}
						#increment boat count
						echo.boatcount = echo.boatcount + 1

						# append to list
						arrayjson.append(writejson)

					#increment pagenumber
					pagenum = pagenum + 1

		#end sailboatlisting_loop


		#Start yachtworld_loop()
		def yachtworld_loop(minprice, maxprice):
			echo.boatcount = 0

			# set base url &  list site
			baseurl='https://www.yachtworld.com/boats-for-sale/type-sail/region-northamerica/'
			echo.listsite= 'Yachtworld.com'

			#set low price
			if minprice == '':
				echo.minpricenum = '30000'
			else:
				echo.minpricenum = minprice
			#print(echo.minpricenum)

			#set high price
			if maxprice == '':
				echo.maxpricenum = '120000'
				maxprice = echo.maxpricenum
			else:
				echo.maxpricenum = maxprice

			pricerange = '&price=' + echo.minpricenum + '-' + echo.maxpricenum
			currlen = '?currency=' + curr + '&length=' + lowlen + '-' + highlen

			# set regions
			wash = 'country-united-states/state-washington/'
			oreg = 'country-united-states/state-oregon/'
			bc = 'country-canada/province-british-columbia/'

			# create list of region url variables
			urllist=[bc,wash,oreg]

			#loop though pages in urllist
			for page in urllist:

				#set urlpath
				urlpath = baseurl+page+currlen+pricerange
				print(urlpath)
				urljson.append(urlpath)

				page = requests.get(urlpath, timeout=5)
				boatpg = BeautifulSoup(page.content, "html.parser")

				# find errors by comparing requested url from listed url
				alert = page
				if page.url != urlpath:
					continue

				# find string with page count in Yachtworld
				pagecountstring=boatpg.find('div', class_="page-selector-text")
				pagecountpattern = re.search('(?<=Viewing )\d{1,2} - (\d{1,2}) of (\d{1,3})',pagecountstring.text)

				# find the two groups that have the item counts
				curritemcount = int(pagecountpattern.group(1))
				totalitemcount = int(pagecountpattern.group(2))

				# set page count
				pagecount = math.ceil(totalitemcount/curritemcount)

				# set first page
				pagenum = 1

				# Loop through pages
				while pagecount >= pagenum:
						# print (pagecount)
						# print (pagenum)

					currpagehtml = urlpath+'&page=' + str(pagenum)
					page = requests.get(currpagehtml, timeout=5)
					boatpg = BeautifulSoup(page.content, "html.parser")
					# print (currpagehtml)

					# find boat listings section
					boatlist = boatpg.find('div', class_="search-right-col")

					#find single boat listing
					boatlisting = boatlist.find_all('a')
					# print(boatlisting)

					#loop though listing and append to list
					for listname in boatlisting:

						if listname['data-reporting-click-listing-type'] != "premium placement":

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
							sizeyear = sizeyear.text
							location = listname.find('div', class_="listing-card-location")
							location = location.text

							#write to json format
							writejson =  {
									"Name": name.text,
									"Price": cost,
									"Size": sizeyear,
									"Location":location,
									"URL": nameurl,
									"Thumb": thumburl,
									"Listing": echo.listsite,
								"Listdate": ''
								}
							#increment boat count
							echo.boatcount = echo.boatcount + 1

							# append to list
							arrayjson.append(writejson)

					#increment pagenumber
					pagenum = pagenum + 1

		# End yachtworld_loop()


#Start Process

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
			sailboatlisting_loop(maxprice)
		elif sitename == "YW":
			yachtworld_loop(minprice, maxprice)
		elif sitename == "both":
			sailboatlisting_loop()
			yachtworld_loop(minprice, maxprice)
			echo.listsite = 'Yachtworld & Sailboatlisting'

		#add Preface list (array)
		arraypreface = []


		preface = {
					'Date': dt_string,
					'urllisting': urljson,
					'Text': 'Results are a search of sailboats in Washington, Oregon and B.C. from ',
					"Listing": echo.listsite,
					'Boatcount': echo.boatcount,
					'Currency': curr,
					'Low': echo.minpricenum,
					'High': maxprice,
					'Short':lowlen,
					'Long': highlen,
					'Creator': 'http://neverforever.ca'
			}
		#append to list
		arraypreface.append(preface)

		# open json file with path
		with open('search_boatlisting/output/boatlist.json', 'w') as outfile:
			#dump two lists with dict names and add formatting (default=str solves date issue)
			json.dump({'fileinfo': arraypreface, 'boats': arrayjson}, outfile, indent=4, default=str)

#write to excel
	import tablib

	datax = tablib.Dataset()
	datax.append_separator(dt_string + ' Currency=' + curr)
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