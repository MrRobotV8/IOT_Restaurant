from telegram.ext import BaseFilter

class KeyboardFilter(BaseFilter):
	def filter(self, message):
		if message.text in ['Book', 'Feedback']:
			return True
		else:
			return False

class KeyRestaurantFilter(BaseFilter):
	def __init__(self, restaurants):
		self.restaurants = restaurants

	def filter(self, message):
		key_restaurant = message.text
		if key_restaurant in list(self.restaurants.keys()):
			return True
		else:
			return False

class PeopleFilter(BaseFilter):
	def filter(self, message):
		try:
			n = int(message.text)
			return True
		except:
			return False
