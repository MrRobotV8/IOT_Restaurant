import pandas as pd
import os
import pyrebase
from collections import OrderedDict
from collections import Counter
import datetime
import json
import random


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

    def upload_booking(self, restaurant_key, hour, n_people, user_id):
        # Check before uploading
        prev_data = self.db.child('restaurants').child(restaurant_key).child('bookings').get().val()
        hash_key = self.hash_creator(user_id, hour, n_people)
        if prev_data is None:
            # No other bookings for that restaurant
            data = {hash_key: user_id}
            self.db.child('restaurants').child(restaurant_key).child('bookings').set(data)

        else:
            # check if user has already bookings for that restaurant
            is_table = self.check_table_availability(restaurant_key, hash_key)

            if is_table:
                data = dict(prev_data)
                data.update({hash_key: user_id})
                self.db.child('restaurants').child(restaurant_key).child('bookings').set(data)
            else:
                # TODO: no tables available; create new path
                print('Your booking was not uploaded')

    # def check_booking(self, data, booking_key):
    #     book_state = True
    #
    #     # check the requested booking vs. the already present ones
    #     date_b, hour_b, n_people_b, user_b = self.unhash(booking_key)
    #
    #     for key in data.keys():
    #         date, hour, n_people, user = self.unhash(key)
    #         if user == user_b:
    #             print('You already have a booking on %s for this restaurant\n' % date)
    #             # Maybe ask if the user want to book
    #             book_state = False
    #     return book_state

    def check_table_availability(self, restaurant_key, hash_key):
        tables = self.download(f'restaurants/{restaurant_key}/details/tables')
        bookings = self.download(f'restaurants/{restaurant_key}/bookings')
        bookings_keys = bookings.keys()
        u_date, u_hour, u_people, u_user = self.unhash(hash_key)
        for k in bookings_keys:
            date, hour, people, user = self.unhash(k)
            if hour == u_hour:
                p = int(people)
                assigned = self.assign_table(p, tables)
                for t in assigned:
                    tables[t] -= 1
        p = str(int(u_people))
        if tables[p] > 0:
            return True
        else:
            return False

    @staticmethod
    def assign_table(people, tables):
        for k, v in tables.items():
            for kk, vv in tables.items():
                if int(k) == people and int(v) > 0:
                    return [k]
                if int(kk) == people and int(vv) > 0:
                    return [kk]
                if (int(v) > 0) and (int(vv) > 0) and (int(kk + k) <= people + 1):
                    return [k, kk]
        return None

    def get_available_tables(self, restaurant_key):
        tables = self.download(f'restaurants/{restaurant_key}/details/tables')
        bookings = self.download(f'restaurants/{restaurant_key}/bookings').keys()
        for b in bookings:
            date, hour, people, user = self.unhash(b)
            assigned = self.assign_table(int(people), tables)
            for t in assigned:
                tables[t] -= 1
        return tables

    @staticmethod
    def hash_creator(user, hour, n_people):
        date = datetime.date.today()
        string = str(date.strftime('%d%m%Y')) + str(hour)
        string = string + str(n_people).zfill(2) + user
        return string

    @staticmethod
    def unhash(key):
        date = "%s/%s/%s" % (key[:2], key[2:4], key[4:8])
        hour = "%s" % (key[8:13])
        n_people = key[13:15]
        user = key[15:]
        print(date, hour, n_people, user)
        return date, hour, n_people, user

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
    # fb.db.child('users').child('Q4RbTEUSanS2k9ErfXaKFdoy6KQ2').child('details').update({'table_key': 'GIGI'})
    fb.get_available_tables('WVqxkU2XXuQ988euCmqbcUvrQfp1')