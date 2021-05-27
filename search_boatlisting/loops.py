#start sailboatlisting_loop
def sailboatlisting_loop(maxprice):

    boatcount = 0

    # set base url &  list site
    baseurl='https://www.sailboatlistings.com/cgi-bin/saildata/db.cgi?db=default&uid=default&websearch=1&view_records=1&sb=date&so=descend'
    listsite = 'Sailboatlisting.com'

    #set low number
    minpricenum ='0'

    #set high price
    if maxprice == '':
        maxpricenum = '120000'
        maxprice = maxpricenum
    else:
        maxpricenum = maxprice

    if curr == "CAD":
        maxpricenum = int(maxpricenum) / exchange
        maxpricenum = str(math.trunc(maxpricenum))

    pricerange = '&price-lt=' + maxpricenum
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
                        "Listing": listsite,
                        "Listdate": datedate
                    }
                #increment boat count
                boatcount = boatcount + 1

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