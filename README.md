# Search-Yachtworld-flask-app
A way to search for boats in the PNW using the Yachtworld website.

## Why
As of their last update (late 2019) [YachtWorld.com](https://yachtworld.com), which is the de facto standard for listing boats, you can no longer search for boats in multiple countries at the same time. The PNW ostensibly includes British Columbia, Washington state and Oregon, so you have to perform 2 separate searches with no way to “save” a previous search and be able to compare.
This flask app scrapes the website and returns results on a web page with links back to the original listing.

## Deployment
Download and run: $ FLASK_APP=/Search-Yachtworld-flask-app/yacht_app flask run  --port 5000 --host=0.0.0.0

## Variables
The search is made based on price (minpricenum, maxpricenum), length (lowlen, highlen), currency (currency) and regions. It loops through each region and writes the results to a json file then appends the results from the next iteration of the loop. 
These variables can be adjusted to suit your needs.
#### line 9 *Set Regions*
* you can add regions using the url parameter from the original site
* be sure to add it to the list as well (line 104)
#### Currency
* Currency defaults to CAD but additional choices can be added in /templates/index.html
#### Other variables
* The Min and Max number can also be adjusted, although at this point they would need to be adjusted in the/templates/index.html as well.
