import pandas as pd
from pyrebase import pyrebase
from pprint import pprint
import datetime
import random 
import json
# https://github.com/thisbejim/Pyrebase 

class Firebase():
	def __init__(self):
		random.seed(200)
		self.config = {
			"apiKey": "AIzaSyDS-H19n86DdyKfqbVhr0-G3llU7vaZjx4",
			"authDomain": "smart-restaurant-project.firebaseapp.com",
			"databaseURL": "https://smart-restaurant-project.firebaseio.com",
			"storageBucket": "smart-restaurant-project.appspot.com"
			}
		self.firebase = pyrebase.initialize_app(self.config)
		
		self.auth = self.firebase.auth()
		self.today = datetime.date.today()
		self.n_bookings = 10
		self.hours = ['2030','1900','2200']
		self.users = {
			'Giannino':'G1xxxx',
			'Pinetto':'P1xxxx',
			'Catastaprulli':'C1xxxx',
			'Gianni':'G2xxxx'}

	def authenticate(self):
		self.user = self.auth.sign_in_with_email_and_password('dan@gmail.com', '123456')
		self.db = self.firebase.database()
		self.DATA = dict(self.db.child('restaurants').get().val())
		# pprint(self.DATA)

	def upload_booking(self, restaurant_key, hash_key):
		#Check before uploading
		prev_data = self.db.child('restaurants').child(restaurant_key).child('Bookings').get().val()
		date, hour, n_people, user_id = self.unhash(hash_key)

		if prev_data == None:
			#No other bookings for that restaurant
			data = {hash_key:user_id}
			self.db.child('restaurants').child(restaurant_key).child('Bookings').set(data)

		else:
			#check if user has already bookings for that restaurant
			book_state = self.check_booking(prev_data, hash_key)

			if book_state:
				#No other bookings for that user
				data = dict(prev_data)
				data.update({hash_key:user_id})
				self.db.child('restaurants').child(restaurant_key).child('Bookings').set(data)
			else: 
				#Other bookings for that user are present in that restaurant
				#TODO: check if user wants to book on another day or wants to cancel booking
				print('Your booking was not uploaded')

	def check_booking(self, data, booking_key):
		book_state = True #remains True if there are not other active reservations 
		print('--------------------------')
		
		#check the requested booking vs. the already present ones 
		date_b, hour_b, n_people_b, user_b = self.unhash(booking_key)

		for key in data.keys():
			date, hour, n_people, user = self.unhash(key)
			if user == user_b:
				print('You already have a booking on %s for this restaurant\n'%(date))
				# Maybe ask if the user want to book
				book_state = False
			print('Attempting on booking with following info:')
			print('day:', date)
			print('hour:', hour)
			print('N° of people:', n_people)
			print('user:', user)
			print('++++++++++')
		return book_state

	def bookings(self, data=None):
		restaurants = [x.key() for x in self.db.child('restaurants').get().each()] #list of restaurants' keys
		# print([x for x in restaurants])
		# self.reset_dataset()

		for x in range(self.n_bookings):
			#INFO for the booking user, randomly chosen
			restaurant = random.choice(restaurants)
			user = random.choice(list(self.users.keys()))
			user_id = self.users[user]
			hour = random.choice(self.hours)
			n_people = random.randint(2,20)

			#INFO hashed in 'hash_key'
			hash_key = self.hash_creator(user_id, hour, n_people)

			#Booking uploading
			self.upload_booking(restaurant, hash_key)

		# pprint(dict(self.db.child('restaurants').get().val()))
		

	def hash_creator(self, user, hour, n_people):
		date = self.today+datetime.timedelta(days=random.randint(0,14))
		string = str(date.strftime('%d%m%Y'))+str(hour)
		string = string+str(n_people).zfill(2)+user
		return string

	def unhash(self, key):
		date = "%s/%s/%s"%(key[:2],key[2:4],key[4:8])
		hour = "%s:%s"%(key[8:10],key[10:12])
		n_people = key[12:14]
		user = key[14:]
		return date, hour, n_people, user

	def reset_dataset(self):
		with open('ordereat-94887-export.json') as f:
			data = json.load(f)	 
		self.db.set(data)
		# pprint(dict(self.db.child('restaurants').get().val()))

FB = Firebase()
FB.authenticate()
FB.bookings()
