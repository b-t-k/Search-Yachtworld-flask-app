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
		sitename=request.form["sitename"]
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

		# set base url &  list site
		if sitename == "SBL":
			baseurl='https://www.sailboatlistings.com/cgi-bin/saildata/db.cgi?db=default&uid=default&websearch=1&view_records=1&sb=date&so=descend'
			listsite= "Sailboatlisting.com"
		elif sitename == "YW":
			baseurl='https://www.yachtworld.com/boats-for-sale/type-sail/region-northamerica/'
			listsite= "Yachtworld.com"

		# input currency
		curr = inputcurr
		#print(curr)

		# input low number
		if sitename == "SBL":
			minpricenum ='0'
		else:
			if minprice == '':
				minpricenum = '30000'
			else:
				minpricenum = minprice
		#print(minpricenum)

		# input high number & convert currency
		exchange = 1.4
		if sitename == "SBL":
			if curr == 'CAD':
				if maxprice == '':
					maxpricenum = 120000 / exchange
					maxpricenum = str(math.trunc(maxpricenum))
				else:
					maxpricenum = float(maxprice) / exchange
					maxpricenum = str(math.trunc(maxpricenum))
			else:
				if maxprice == '':
					maxpricenum = '120000'
				else:
					maxpricenum = maxprice
		else:
			if maxprice == '':
				maxpricenum = '120000'
			else:
				maxpricenum = maxprice
		#print(maxpricenum)

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

		# set variables
		if sitename == "SBL":
			pricerange = '&price-lt=' + maxpricenum
			boatlength = '&length-gt=' + lowlen + '&length-lt=' + highlen

			# create list of url variables
			bc = '&city=bc'
			van = '&city=vancouver'
			british = '&city=british%20columbia'
			wash = '&state=Washington'

			# create list of region url variables
			urllist=[bc,van,british,wash]

		elif sitename == "YW":
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
		#print (path_folder)

		boatcount = 0

		# set date and time
		now = datetime.now()
		dt_string = now.strftime("%B %d, %Y %H:%M")

		# create empty list
		arrayjson = []
		urljson =[]
		#loop though pages in urllist
		for page in urllist:
		# get url
			if sitename == "SBL":
				urlpath = baseurl+boatlength+pricerange+page
				#print(urlpath)
			elif sitename == "YW":
				urlpath = baseurl+page+currlen+pricerange

			urljson.append(urlpath)


			page = requests.get(urlpath, timeout=5)
			boatpg = BeautifulSoup(page.content, "html.parser")

			# find errors by comparing requested url from listed url
			alert = page
			if page.url != urlpath:
				continue

			if sitename == "SBL":
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

				while pagecount >= pagenum:
					#print (pagecount)
					#print (pagenum)

					currpagehtml = urlpath+'&nh=' + str(pagenum)
					page = requests.get(currpagehtml, timeout=5)
					boatpg = BeautifulSoup(page.content, "html.parser")
					#print (currpagehtml)

#LOOP

					boatlist = boatpg.find_all('table', attrs={'width':'728'})

					#loop though listing and append to list
					for listname in boatlist:
						thumbimg = listname.find('img')
						thumb=thumbimg['src']

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
								"URL": nameurl,
								"Name": name.text,
								"Price": cost,
								"Size": sizeyear,
								"Location":location,
								"Thumb": thumburl,
								"Listing": listsite,
								"Listdate": datedate
							}
						#increment boat count
						boatcount = boatcount + 1
						# append to list
						arrayjson.append(writejson)

#END LOOP

					#increment pagenumber
					pagenum = pagenum + 1

			elif sitename == "YW":

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
#					print (pagecount)
#					print (pagenum)

					currpagehtml = urlpath+'&page=' + str(pagenum)
					page = requests.get(currpagehtml, timeout=5)
					boatpg = BeautifulSoup(page.content, "html.parser")
#					print (currpagehtml)

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
						sizeyear = sizeyear.text
						location = listname.find('div', class_="listing-card-location")
						location = location.text

						#write to json format
						writejson =  {
								"URL": nameurl,
								"Name": name.text,
								"Price": cost,
								"Size": sizeyear,
								"Location":location,
								"Thumb": thumburl,
								"Listing": listsite
							}
						#increment boat count
						boatcount = boatcount + 1

						# append to list
						arrayjson.append(writejson)

					#increment pagenumber
					pagenum = pagenum + 1

		#add Preface list (array)
		arraypreface = []

		preface = {
					'Date': dt_string,
					'urllisting': urljson,
					'Text': 'Results are a search of sailboats in Washington, Oregon and B.C. from ',
					"Listing": listsite,
					'Boatcount': boatcount,
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


