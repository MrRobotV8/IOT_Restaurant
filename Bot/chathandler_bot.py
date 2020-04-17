from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import ConversationHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import json
import functions
from BotFilters import *
from RestaurantPublisher import Publisher
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)
class SmartRestaurant():
	def __init__(self):
		self.initial_keyboard = [['Book', 'Order', 'Feedback'], ['Wait', 'CheckOut']]
		self.time_booking = [['19:00', '19:30', '20:00'], ['20:30', '21:00', '21:30']]

		self.customers_path = 'Customers.json'
		self.customers = functions.open_json(self.customers_path)
		self.restaurants = functions.open_json('Restaurants.json')

		self.keyboard_filter = KeyboardFilter()
		self.people_filter = PeopleFilter()
		self.key_restaurant_filter = KeyRestaurantFilter(self.restaurants)

		self.START, self.COND_1, self.BOOK, self.CHECK_BOOKING, self.ORDER, self.FEED, self.WAIT, self.CHECK, self.PEOPLE, self.TIME = range(10)
		self.STATE = self.START

	def start(self, bot, update):
		self.user_id = str(bot.message.from_user.id)
		message = 'Welcome to the StartRestaurantBot. Select one of the following functions'
		reply_markup = ReplyKeyboardMarkup(self.initial_keyboard, one_time_keyboard=False, resize_keyboard=True)
		bot.message.reply_text(message, reply_markup=reply_markup)

		return self.COND_1

	def cond1(self, bot, update):
		selection = bot.message.text
		if selection == 'Book':
			return self.BOOK
		elif selection == 'Order':
			return self.ORDER
		elif selection == 'Feedback':
			print('feedback')
			message = 'Tap if you want to change the room_temperature'
			reply_markup = ReplyKeyboardMarkup([['Lower', 'Raise', 'Good']], one_time_keyboard=True, resize_keyboard=True)
			bot.message.reply_text(message, reply_markup=reply_markup)
			return self.FEED
		elif selection == 'Wait':
			return self.Wait
		elif selection == 'CheckOut':
			return self.CHECK

	def book(self, bot, update):
		message = 'At which Restaurant do you want to book a table? Select from the list the corresponding key'
		bot.message.reply_text(message)
		for i in functions.keys_restaurants(self.restaurants):
			new_restaurant = f'{i[1]} -> {i[0]}'
			bot.message.reply_text(new_restaurant)

		return self.CHECK_BOOKING

	def check_booking(self, bot, update):
		self.key_restaurant = bot.message.text
		restaurant_obj = self.restaurants[self.key_restaurant]
		customers_restaurant = list(restaurant_obj.keys())

		if self.user_id in customers_restaurant:
			print('Already Booked')
			message = 'You already have a booking'
		else:
			print('Booking Phase')
			message = 'For how many people? Type the number'
			bot.message.reply_text(message)

			return self.PEOPLE

	def people(self, bot, update):
		self.people = int(bot.message.text)
		message = 'Let us now know the time. Select form the keyboard'
		reply_markup = ReplyKeyboardMarkup(self.time_booking, one_time_keyboard=True, resize_keyboard=True)
		bot.message.reply_text(message, reply_markup=reply_markup)

		return self.TIME

	def time(self, bot, update):
		self.time_selected = bot.message.text
		functions.update_customers(self.user_id, self.people, self.time_selected, self.key_restaurant, self.customers, self.restaurants)
		print('SAVED')

		message = f'Your booking has been saved. See you at {self.time_selected} in {self.restaurants[self.key_restaurant]["name"]}'
		restart = 'Type /start if you want to select other features'
		bot.message.reply_text(message)
		bot.message.reply_text(restart)
		return ConversationHandler.END

	def order(self, bot, update):
		message = 'Click on the link to begin the ordering phase'

	def feedback(self, bot, update):
		feeling = bot.message.text
		feedback_key = self.customers[self.user_id]['active_booking']['key']
		topic = f"Temperature_{feedback_key}"
		pub = Publisher(clientID=self.user_id, topic=topic)
		pub.publish(feeling)


	def help_(self):
		print('AAA')

	def main(self):
		updater = Updater('892866853:AAF3W2Dns7-Koiayk-2fuDgIDiFCfrLEfLw', use_context=True)

		# Get the dispatcher to register handlers:
		dp = updater.dispatcher
		conv_handler = ConversationHandler(
			entry_points=[CommandHandler('start',self.start)],
			states={
				self.COND_1: [MessageHandler(self.keyboard_filter, self.cond1)],
				self.BOOK: [MessageHandler(Filters.text, self.book)],
				self.CHECK_BOOKING: [MessageHandler(self.key_restaurant_filter, self.check_booking)],
				self.PEOPLE: [MessageHandler(self.people_filter, self.people)],
				self.TIME: [MessageHandler(Filters.text, self.time)],
				self.FEED: [MessageHandler(Filters.text, self.feedback)]
				
			},
			fallbacks=[CommandHandler('help',self.help_),
						# CommandHandler('cancel', self.cancel)
						],
			allow_reentry=True
		)

		dp.add_handler(conv_handler)
		updater.start_polling()
		updater.idle()

if __name__ == '__main__':
	sr = SmartRestaurant()
	sr.main()





