import pickle
from models import *

def create_pickle(flight_to_bid):
    flights = mongo.db.flights
    pickle_name = flight_to_bid+'.pickle'
    if not pickle_name:
        pickle_empty_file = open(pickle_name,'wb')
        
        pickle_empty_file.close()
