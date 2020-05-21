# Search-boatlisting-flask-app
A way to search for boats in the PNW using the Yachtworld website.

## Why
As of their last update (late 2019) [YachtWorld.com](https://yachtworld.com), which is the de facto standard for listing boats, you can no longer search for boats in multiple countries at the same time. The PNW ostensibly includes British Columbia, Washington state and Oregon, so you have to perform 2 or 3 separate searches with no way to “save” one region's search and aggregate the results.
It also occurred to me that [sailboatlistings.com](https://sailboatlistings.com) is also a popular venue for selling boats and also has a variety of boats not found on Yachtworld.
The latest version of this flask app scrapes the Yachtworld website as well as the Sailboatlistings site and returns desired results on a local web page with links back to the original listing.

## What
Currently this app searches Yachtworld for BC, Washington and Oregon. Since the Sailboalistings site is set up badly for non U.S. boats, on that it searches for a combination of BC, British Columbia, Vancouver, Washington and Oregon.
The results are displayed with links back to the originating site and also output to /output/boatlist.json and that file can be saved for other uses by copying it out of the folder.

## Deployment
Download and run: $ FLASK_APP=/Search-boatlisting-flask-app/yacht_app flask run  --port 5000 --host=0.0.0.0
The app will run in the background (on OSX, you will need to keep the terminal window open as long as you are running the app. Type Ctrl-c to quit). Results can be found at [http://localhost:5000](http://localhost:5000).
#### Dependencies
Obviously python and flask must be installed on your computer for this to run. You will also need to install the BeautifulSoup4 and Requests packages.
#### WARNING
[Flask warns](https://flask.palletsprojects.com/en/1.1.x/deploying/#deployment) that "While lightweight and easy to use, Flask’s built-in server is not suitable for production as it doesn’t scale well." I imagine there might be security concerns as well. But for local use it works just fine.

## Variables
The search is made based on price (minpricenum, maxpricenum), length (lowlen, highlen), currency (currency) and regions. It loops through each region and writes the results to a json file then appends the results from the next iteration of the loop.
There is also a "best before" date for the sailboatlistings as this site often suffers from outdated listings. It is currently set to  January 1, 2018 (bestbefore = datetime(2018, 1, 1)) (~line 223).
These variables can be adjusted to suit your needs.
* Note: Sailboatlistings doesn't accept a minimum price variable
#### *Set Regions* Sailboatlistings
* The list of city & state variables (line 120) can be modified or deleted.
* Be sure to also add the variables to the urllist[] array (line 126)
#### *Set Regions* Yachtworld
* The base url for Yachtworld (line 62) is set to 'https://www.yachtworld.com/boats-for-sale/type-sail/region-northamerica/'. Areas out of North America will need to reset this.
* you can add regions using the url parameter from the original site
* be sure to add them to the list (line 133) and the variables to the urllist[] array (line 138)
#### Currency
* Currency defaults to CAD but additional choices can be added in /templates/index.html
#### Other variables
* The Min and Max numbers can also be adjusted, although at this point they would need to be adjusted in the/templates/index.html as well.
