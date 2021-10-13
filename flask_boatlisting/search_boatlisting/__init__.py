from flask import Flask

app = Flask(__name__)
#set key for security validation
app.config['SECRET_KEY'] = 'safa33rafsdasd'

# import From the package (folder) named search_boatlisting
from search_boatlisting import routes