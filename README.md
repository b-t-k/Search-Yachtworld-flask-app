# Search-Yachtworld-flask-app
A way to search for boats in the PNW using the Yachtworld website.

## Why
As of their last update (late 2019) [YachtWorld.com](https://yachtworld.com), which is the de facto standard for listing boats, you can no longer search for boats in multiple countries at the same time. The PNW ostensibly includes British Columbia, Washington state and Oregon, so you have to perform 2 or 3 separate searches with no way to “save” one region's search and aggregate the results.
This flask app scrapes the website and returns desired results on a local web page with links back to the original listing.

## Deployment
Download and run: $ FLASK_APP=/Search-Yachtworld-flask-app/yacht_app flask run  --port 5000 --host=0.0.0.0
The app will run in the background (on OSX, you will need to keep the terminal window open as long as you are running the app. Type Ctrl-c to quit). Results can be found at [http://localhost:5000](http://localhost:5000).
#### Dependencies
Obviously python and flask must be installed on your computer for this to run. You will also need (more soon).
#### WARNING
[Flask warns](https://flask.palletsprojects.com/en/1.1.x/deploying/#deployment) that "While lightweight and easy to use, Flask’s built-in server is not suitable for production as it doesn’t scale well." I imagine there might be security concerns as well. But for local use it works just fine.

## Variables
The search is made based on price (minpricenum, maxpricenum), length (lowlen, highlen), currency (currency) and regions. It loops through each region and writes the results to a json file then appends the results from the next iteration of the loop.
These variables can be adjusted to suit your needs.
#### line 9 *Set Regions*
* The base url (line 56) is set to 'https://www.yachtworld.com/boats-for-sale/type-sail/region-northamerica/'. Areas out of North America will need to reset this.
* you can add regions using the url parameter from the original site
* be sure to add them to the list as well (line 104)
#### Currency
* Currency defaults to CAD but additional choices can be added in /templates/index.html
#### Other variables
* The Min and Max numbers can also be adjusted, although at this point they would need to be adjusted in the/templates/index.html as well.
