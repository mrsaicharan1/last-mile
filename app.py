#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, session, redirect, url_for, flash
import bcrypt
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
from models import *
import redis    
import operator
import pickle
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
sorted_bids={}
top_bids = {}

@app.route('/index')
def index():
    pass

@app.route('/signup',methods=['POST','GET'])
def signup():
     # store hashed password and credentials for POST request
    if request.method == 'POST': # if data is being POSTed
        users = mongo.db.users
        for user in users.find(): # looping through the users
            if user['username'] == request.form['username']:# check if the entered username matches to avoid collisions
                flash('Username already exists. Please pick another one')
                return redirect(url_for('signup'))

            elif len(request.form['password'])<8: # password length check
                flash('Please provide a password which is atleast 8 characters long')
                return redirect(url_for('signup'))

            elif request.form['password']!=request.form['repeat_password']: # check passwords match
                flash('Passwords mismatch. Please try again')
                return redirect(url_for('signup'))
 # if no exception, go here
        hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt(10)) # hashing the password with a salt
        users.insert({'email':request.form['email'],'username':request.form['username'],'password':hashed_password.decode('utf-8')})# storing the hashed password in the collection

        flash('Signup Success!') # flash messages
        return redirect(url_for('signin'))
    # render form for GET
    return render_template('forms/signup.html')


@app.route('/signin',methods=['POST','GET'])
def signin():
     # check if hashes match and set session variables
    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'username':request.form['username']})
        if bcrypt.hashpw(request.form['password'].encode('utf-8'),user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('get_flight_details'))
        else:
            flash('Incorrect Credentials Entered')
            return redirect(url_for('signin'))
    return render_template('forms/signin.html')

@app.route('/')
def home():
    return render_template('pages/index.html')
@app.route('/forgot')
def forgot():
   pass

@app.route('/register')
def register():
   pass

@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

@app.route('/get_flight_details',methods=['POST','GET'])
def get_flight_details():
    if not session['username']:
        return redirect(url_for('signin'))
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
                read_top_bids = open('top_bids.pickle','rb')
                top_bids = pickle.load(read_top_bids)
                read_top_bids.close()
                return render_template('forms/bidding_page.html',flight_to_bid = flight_to_bid,top_bids=top_bids)
            else:
                flash('Could not find a booking pertaining to the entered reference number')
                return redirect(url_for('get_flight_details'))  
    return render_template('forms/details.html')
        # if request.form['reference'][0:2] =='EK':
        #     flight_to_bid=flights.find_one({'airline':'Emirates'})
        #     return redirect(url_for('bidding',flight_to_bid=flight_to_bid))

@app.route('/bidding_logic',methods=['POST','GET'])
def bidding_logic():
    if request.method == 'POST':
        
        read_top_bids = open('top_bids.pickle','rb')
        top_bids = pickle.load(read_top_bids)
        read_top_bids.close()

        top_bids[session['username']] = request.form['business-bid-amount']
        top_bids_reversed = {v:k for k,v in top_bids.items() }
        top_bids_sorted = {key:top_bids_reversed[key] for key in sorted(top_bids_reversed.keys())}
        top_bids= {k:v for k,v in top_bids.items()}
        
        write_top_bids = open('top_bids.pickle','wb')
        pickle.dump(top_bids,write_top_bids)
        write_top_bids.close()

        flights = mongo.db.flights
        airlines = mongo.db.airlines
        confirmed_info = mongo.db.confirmed_tickets
        for confirmed in confirmed_info.find():
            if session['reference'] == confirmed['reference']:
                print(session['reference'])
                print(confirmed['reference'])
                flight_to_bid = flights.find_one({'flight_id':confirmed['linked_flight']})
                print(flight_to_bid)
                return render_template('forms/bidding_page.html',flight_to_bid = flight_to_bid,top_bids=top_bids)
    





    
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
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
