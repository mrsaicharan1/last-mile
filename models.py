from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'last-mile'
app.config['MONGO_URI'] = 'mongodb://lastmile:lastmile1@ds139534.mlab.com:39534/last-mile'

mongo = PyMongo(app)