import pandas as pd
import os
import pyrebase
from collections import OrderedDict
from collections import Counter
import numpy as np
import json


class Firebase:
    def __init__(self):
        self.config = {
            'apiKey': "AIzaSyCNUQyDSE8LglsRzQGpk8OJGvTj2IyicT4",
            'authDomain': "ordereat-94887.firebaseapp.com",
            'databaseURL': "https://ordereat-94887.firebaseio.com",
            'projectId': "ordereat-94887",
            'storageBucket': "ordereat-94887.appspot.com",
            'messagingSenderId': "89417842986",
            'appId': "1:89417842986:web:162875424095cecd65de53",
            'measurementId': "G-BHVSYJK293"
          }
        self.firebase = pyrebase.initialize_app(self.config)

    def authenticate(self):
        """
            Authentication: allows to access the database
        """
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()

    def download(self, field):
        """
            input :
                'field' = string : should take only 3 values
            output :
                'data_list' = list : list of all the elements in a given field
        """
        all_data = self.db.child(field).get()
        obj = {}
        for e in all_data.each():
            obj[e.key()] = e.val()
        return obj

    def upload(self, field, data2upload, key=None):
        """
            input :
                'field' = string : should take only 3 values
                'data2upload' = json : file to upload on the DB
        """
        self.db.child(field).child(key).set(data2upload)

    def most_frequent(self, List, n):
        occurence_count = Counter(List)
        return occurence_count.most_common(n)

    # def specific_download(self, field, reference, n=1):
    #     activity_times = [
    #         '10 min', '10-20 min', '20-30 min',
    #         '30-60 min', '1-2 h', '2-3 h',
    #         '3-8 h', '>8 h'
    #     ]
    #     modes = ['unknown_activity_type', 'Car', 'Walk', 'Bike',
    #              'Bus/Tram', 'in_passenger_vehicle', 'Train', 'in_bus', 'Subway',
    #              'flying', 'motorcycling', 'running']
    #
    #     query = self.db.child(field).order_by_child("user_id").equal_to(reference).get().val()
    #
    #     pretty_query = ''
    #     categories = []
    #     destinations = []
    #     for i in query.values():
    #         categories.append(i['category'])
    #         destinations.append(i['D']['name'])
    #         s = f"From {i['O']['name']} to {i['D']['name']} for {activity_times[i['activity_time']]} by {modes[i['mode']]}\n"
    #         pretty_query += s
    #
    #     n_trips = len(query)
    #     most_categories = self.most_frequent(categories, n)
    #     most_destinations = self.most_frequent(destinations, n)
    #
    #     return pretty_query, n_trips, most_categories, most_destinations


if __name__ == '__main__':
    fb = Firebase()
    fb.authenticate()
    # fb.download('restaurants')
    obj = {
        'details': {
            'name': 'GIGGI'
        }
    }
    new_user = fb.db.child('users').push(obj)
    print(new_user)
    print(new_user.key)