#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, session, redirect, url_for
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
sorted_bids={}
@app.route('/index')
def index():
    pass

@app.route('/')
def home():
    return render_template('pages/index.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        pass

    return render_template('forms/login.html')    

@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/get_flight_details',methods=['POST','GET'])
def get_flight_details():
    if request.method == 'POST':
        session['reference'] = request.form['reference']
        flights = mongo.db.flights
        airlines = mongo.db.airlines
        confirmed_info = mongo.db.confirmed_tickets
        for confirmed in confirmed_info.find():
            print(confirmed['reference'])
            if request.form['reference'] == confirmed['reference']:
                print(request.form['reference'])
                print(confirmed['reference'])
                flight_to_bid = flights.find_one({'flight_id':confirmed['linked_flight']})
                print(flight_to_bid)
                return render_template('forms/bidding_page.html',flight_to_bid = flight_to_bid)
    else:   
        return render_template('forms/details.html')
        # if request.form['reference'][0:2] =='EK':
        #     flight_to_bid=flights.find_one({'airline':'Emirates'})
        #     return redirect(url_for('bidding',flight_to_bid=flight_to_bid))


@app.route('/bidding',methods=['POST','GET'])
def bidding():
        return render_template('forms/bidding_page.html',flight_to_bid = session.get('flight_to_bid'))

# Error handlers.
@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
