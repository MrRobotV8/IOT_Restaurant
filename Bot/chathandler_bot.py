from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import ConversationHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import json
import functions
from BotFilters import *
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)
class SmartRestaurant():
	def __init__(self):
		self.keyboard_filter = KeyboardFilter()


		self.initial_keyboard = [['Book', 'Order', 'Feedback'], ['Wait', 'CheckOut']]
		self.time_booking = [['19:00', '19:30', '20:00'], ['20:30', '21:00', '21:30']]
		self.customers_path = 'Customers.json'
		self.customers = functions.open_json(self.customers_path)

		self.START, self.COND_1, self.BOOK, self.ORDER, self.FEED, self.WAIT, self.CHECK, self.PEOPLE, self.TIME = range(9)
		self.STATE = self.START

	def start(self, bot, update):
		self.user_id = bot.message.from_user.id
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
			return self.FEED
		elif selection == 'Wait':
			return self.Wait
		elif selection == 'CheckOut':
			return self.CHECK

	def book(self, bot, update):
		# user_id = bot.message.from_user.id
		customers_booked = self.customers.keys()
		if self.user_id in customers_booked:
			message = 'You already have a table booked'
			bot.update.reply_text(message)
			ConversationHandler.END
			return 
		else:
			message = 'Welcome to the booking phase, please let us know for how many people are you booking'
			bot.message.reply_text(message)

			return self.PEOPLE

	def people(self, bot, update):
		self.people = bot.message.text
		message = 'Let us now know the time'
		reply_markup = ReplyKeyboardMarkup(self.time_booking, one_time_keyboard=True, resize_keyboard=True)
		bot.update.reply_text(message, reply_markup=reply_markup)

		return self.TIME

	def time(self, bot, update):
		self.time_selected = bot.message.text
		functions.update_customers(self.user_id, self.people, self.time_selected, self.customers)
		print('SAVED')


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
				self.PEOPLE: [MessageHandler(self.people_filter, self.people)],
				self.TIME: [MessageHandler(self.time_filter, self.time)]
				
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





