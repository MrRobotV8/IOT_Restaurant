"""
Main of the TelegramBot. It is created as a class with states, following the guidelines of the telegram-api docs.
Each state of the telegram is connected to a function handling two parameters: bot and update of the imported
class Updater.
"""
import traceback
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import ConversationHandler, Filters
from telegram import ReplyKeyboardMarkup
import logging
import os
from functions import *
from BotFilters import *
from Firebase import Firebase
import datetime
from FeedbackSender import Sender

# Enable logging for displaying prints
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# PORT where exposing the telegram, needed for continuously run on the heroku server
with open('../catalog.json', 'r') as f:
    CONFIG = json.loads(f.read())

HEROKU = CONFIG['heroku']
PORT = int(os.environ.get('PORT', HEROKU['port']))


class TelegramBot:
    def __init__(self):
        logger.info('TelegramBot started')
        self.token = CONFIG['bot_telegram']['token']
        self.heroku_link = HEROKU['base_link']
        self.order_link = HEROKU['order_link']
        self.app_name = HEROKU['app_name']
        self.fb = Firebase()
        self.sender = Sender()
        self.fb.authenticate()
        # self.fb.listener()
        self.restaurants = self.fb.download('restaurants')
        self.restaurants_names = [r['details']['name'] for r in self.restaurants.values()]
        self.restaurants_mapper = {self.restaurants_names[i]: list(self.restaurants.keys())[i]
                                   for i in range(len(self.restaurants_names))}

        self.initial_keyboard = [['Book', 'Order', 'Feedback'], ['Join', 'Wait', 'CheckOut'], ['Info']]
        self.time_booking = [['19:00', '19:30', '20:00'], ['20:30', '21:00', '21:30']]

        self.email_filter = EmailFilter()
        self.keyboard_filter = KeyboardFilter()
        self.people_filter = PeopleFilter()
        self.key_restaurant_filter = KeyRestaurantFilter(self.restaurants_names)

        # states of the telegram bot
        n_states = 18
        self.START, self.START_RETURN, self.COND_1, self.EMAIL, self.PASSWORD, \
        self.PASSWORD_2, self.NICK, self.SIGN_IN, self.CHECK_SIGN, self.CHECK_BOOKING, \
        self.ORDER, self.FEED, self.JOIN, self.CHECK, \
        self.PEOPLE, self.TIME, self.INFO, self.DELETE_BOOKING = range(n_states)
        self.STATE = self.START

    def check_signin(self):
        users = self.fb.download('users')
        for k, v in users.items():
            try:
                if v['details']['bot_id'] == self.user_id:
                    self.fb_id = k
                    return True
            except:
                pass
        else:
            return False

    def start_return(self, bot, update):
        message = 'Welcome back. Please select one of the following.'
        reply_markup = ReplyKeyboardMarkup(self.initial_keyboard, one_time_keyboard=True, resize_keyboard=True)
        bot.message.reply_text(message, reply_markup=reply_markup)

        return self.COND_1

    def start(self, bot, update):
        self.user_id = str(bot.message.from_user.id)
        logger.info(f'{self.user_id} STARTED Bot')
        if self.check_signin():
            logger.info(f'{self.user_id} Already Signed-Up')
            if self.fb.db.child('users').child('active').child('restaurant_key').get():
                self.restaurant_key = self.fb.db.child('users').child('active').child('restaurant_key').get().val()
            message = 'Welcome back. Please select one of the following.'
            reply_markup = ReplyKeyboardMarkup(self.initial_keyboard, one_time_keyboard=True, resize_keyboard=True)
            bot.message.reply_text(message, reply_markup=reply_markup)
            return self.COND_1
        else:
            logger.info(f'{self.user_id} Creation Account')
            message = 'Welcome to OrderEat. This bot will allow you to BOOK, ORDER, INTERACT with' \
                      'Restaurants subscribed to our service.\n' \
                      'Create an account or insert your credentials if you already have one.'
            reply_markup = ReplyKeyboardMarkup([['Create Account', 'Sign-In']], one_time_keyboard=True,
                                               resize_keyboard=True)
            bot.message.reply_text(message, reply_markup=reply_markup)

            return self.CHECK_SIGN

    def check_sign(self, bot, update):
        logger.info(f'{self.user_id} sent: {bot.message.text}')
        if bot.message.text == 'Create Account':
            self.new = True
            bot.message.reply_text('Please Inert your email')
            return self.EMAIL
        else:
            self.new = False
            bot.message.reply_text('Insert your email')
            return self.EMAIL

    def email(self, bot, update):
        logger.info(f'{self.user_id} sent: {bot.message.text}')
        self.email = bot.message.text
        if self.new:
            message = 'Insert your Nickname'
            bot.message.reply_text(message)
            return self.NICK
        else:
            message = 'Insert your password'
            bot.message.reply_text(message)
            return self.PASSWORD

    def nickname(self, bot, update):
        logger.info(f'{self.user_id} sent: {bot.message.text}')
        self.nickname = bot.message.text
        message = 'Insert now your password'
        bot.message.reply_text(message)

        return self.PASSWORD

    def password(self, bot, update):
        logger.info(f'{self.user_id} sent: {bot.message.text}')
        self.password = bot.message.text
        if self.new:
            message = 'Insert again'
            bot.message.reply_text(message)
            return self.PASSWORD_2
        else:
            if self.sign_in():
                message = 'Welcome back. Please select one of the following.'
                reply_markup = ReplyKeyboardMarkup(self.initial_keyboard, one_time_keyboard=True, resize_keyboard=True)
                bot.message.reply_text(message, reply_markup=reply_markup)
                return self.COND_1
            else:
                message = 'Wrong Credentials.'
                reply_markup = ReplyKeyboardMarkup([['Create Account', 'Sing-In']], one_time_keyboard=True,
                                                   resize_keyboard=True)
                bot.message.reply_text(message, reply_markup=reply_markup)
                return self.CHECK_SIGN

    def password_2(self, bot, update):
        logger.info(f'{self.user_id} sent: {bot.message.text}')
        if bot.message.text == self.password:
            self.sign_up()
            message = 'You have been signed-up!'
            bot.message.reply_text(message)

            return self.START_RETURN
        else:
            logger.info(f'Password are not the same')
            message = 'Your passwords do not coincide. Reinsert your password.'
            bot.message.reply_text(message)

            return self.PASSWORD

    def sign_up(self):
        user = self.fb.auth.create_user_with_email_and_password(self.email, self.password)
        uid = user['localId']
        data = {
            'mail': self.email,
            'name': self.nickname,
            'is_bot': 1,
            'bot_id': self.user_id,
        }

        logger.info(f'{self.user_id} successfully singed-up.\nNew entry on the Firebase.\nPayload to Firebase: {data}')
        self.fb.db.child('users').child(uid).child('details').set(data)

    def sign_in(self):
        try:
            user = self.fb.auth.sign_in_with_email_and_password(self.email, self.password)
            self.fb_id = user['localId']
            ref = self.fb.db.child('users').child(self.fb_id)
            ref.update({'bot_id': self.user_id})
            return True
        except:
            traceback.print_exc()
            return False

    def cond1(self, bot, update):
        logger.info(f'{self.user_id} sent: {bot.message.text}')
        selection = bot.message.text
        if selection == 'Book':
            logger.info(f'BOOK: selection of restaurant')
            message = 'At which Restaurant do you want to book a table?'
            bot.message.reply_text(message)
            sorted_restaurants = sorted(self.restaurants_names)
            for i in sorted_restaurants:
                new_restaurant = i
                bot.message.reply_text(new_restaurant)
            return self.CHECK_BOOKING

        elif selection == 'Order':
            user = self.fb.db.child('users').child(self.fb_id).child('active').get().val()
            if user is not None:
                logger.info(f'ORDER: {self.user_id} has already a booking and now can click on the order page')
                restaurant = self.fb.db.child('users').child(self.fb_id).child(
                    'active').child('restaurant_key').get().val()
                message = 'Click on the link to begin the ordering phase'
                if user['is_booker'] == 1:
                    link = f'{self.order_link}{self.fb_id}/{restaurant}'
                else:
                    booker = user['booker']
                    link = f'{self.order_link}{booker}/{restaurant}'
                self.link = link
                bot.message.reply_text(message)
                bot.message.reply_text(link)

                return self.START_RETURN
            else:
                logger.info(f'ORDER: {self.user_id} does not have any bookings. Redirect to the start')
                message = 'You do not have any active bookings. First create a booking'
                bot.message.reply_text(message)
                return self.START_RETURN

        elif selection == 'Feedback':
            user = self.fb.db.child('users').child(self.fb_id).child('active').get().val()
            if user is not None:
                logger.info(f'FEEDBACK: {self.user_id} can notify the restaurant owner of his desire to change '
                            f'the temperature')
                message = 'Tap if you want to change the room_temperature'
                reply_markup = ReplyKeyboardMarkup([['Lower', 'Raise', 'Good']], one_time_keyboard=True,
                                                   resize_keyboard=True)
                bot.message.reply_text(message, reply_markup=reply_markup)
                return self.FEED
            else:
                logger.info(f'FEEDBACK: {self.user_id} does not have any bookings. Redirect to the start')
                message = 'You do not have any active bookings. First create a booking'
                bot.message.reply_text(message)
                return self.START_RETURN

        elif selection == 'Join':
            message = 'You chose to JOIN a Table. Please insert the relative KEY'
            bot.message.reply_text(message)
            return self.JOIN

        elif selection == 'Wait':
            restaurant_key = self.fb.db.child(f'users/{self.fb_id}/active/restaurant_key').get().val()
            order = self.fb.db.child(f'orders/{self.fb_id}/{restaurant_key}').get().val()
            if restaurant_key is None:
                message = 'You do not an active booking. Please start again.'
                bot.message.reply_text(message)
                return self.START_RETURN
            if order is None:
                message = 'You do not have placed an order yet. Please start again and select ORDER.'
                bot.message.reply_text(message)
                return self.START_RETURN
            if order is not None and restaurant_key is not None:
                last_order_key = list(order.keys())[-1]
                # last_order = order[last_order_key]
                # TODO: change data type
                date = datetime.datetime.strptime(last_order_key, '%d%m%Y%H%M%S')
                if date < (datetime.datetime.now() - datetime.timedelta(days=1)):
                    message = 'Your last order is too old. Please start again and select ORDER'
                    bot.message.reply_text(message)
                    return self.START_RETURN
                else:
                    active_customers = self.fb.db.child(f'restaurants/{restaurant_key}/customers').get().val()
                    n_active = len(list(active_customers.values()))
                    # M/M/m queue but not so much
                    f = 20 if n_active < 3 else 20 + 20 / 3 * n_active
                    message = f'There are {n_active} customers before you.\n' \
                              f'Your waiting time is approximately {int(f)} minutes'
                    bot.message.reply_text(message)
                    return self.START_RETURN

        elif selection == 'CheckOut':
            history_order, check = self.checkout()
            message = f'Your History Order: {history_order}\nYour Total: {check}\nThanks and return soon!'
            bot.message.reply_text(message)

            return self.CHECK

        elif selection == 'Info':
            logger.info(f'INFO: {self.user_id} requested info about restaurant')
            restaurant = self.fb.db.child(f'users/{self.fb_id}/active/restaurant_key').get().val()
            if restaurant is not None:
                token = self.fb.db.child(f'restaurants/{restaurant}/details/token_order').get().val()
                response = self.sender.get_device_telemetry(token)
                json_response = json.loads(response.text)
                try:
                    message = f'TEMPERATURE: {json_response["temperature"][-1]["value"]}°C\n' \
                              f'HUMIDITY: {json_response["humidity"][-1]["value"]}%\n' \
                              f'NOISE: {json_response["noise"][-1]["value"]}dB'
                    bot.message.reply_text(message)
                except:
                    message = 'No Info can be retrieved. Sensors are not yet deployed.'
                    bot.message.reply_text(message)
            else:
                message = 'You are not booked.'
                bot.message.reply_text(message)

            return self.START_RETURN

        elif selection == 'Help':
            restaurant = self.fb.db.child(f'users/{self.fb_id}/active/restaurant_key').get().val()
            if restaurant is not None:
                message = 'Your request has been accepted. A waiter will come to you as soon as possible'
                token = self.fb.db.child(f'restaurants/{restaurant}/details/token_order').get().val()
                tables = self.fb.db.child(f'users/{self.fb_id}/active/table_id').get().val()
                for i, t in tables.items():
                    self.sender.send(f'{token}_item:table:{t}', {'reserved': False}, 'attributes')
                bot.message.reply_text(message)

    def check_booking(self, bot, update):
        logger.info(f'BOOK: {self.user_id} sent: {bot.message.text}')
        restaurant_chosen = bot.message.text
        self.restaurant_name = restaurant_chosen
        self.restaurant_key = self.restaurants_mapper[restaurant_chosen]
        if self.fb.db.child(f'users/{self.fb_id}/active').get().val() is not None:
            logger.info(f'BOOK: {self.user_id} already has a booking in the restaurant')
            message = f'You already have a Booking at {restaurant_chosen}. Do you want to delete it?'
            reply_markup = ReplyKeyboardMarkup([['YES', 'NO']], one_time_keyboard=True, resize_keyboard=True)
            bot.message.reply_text(message, reply_markup=reply_markup)
            return self.DELETE_BOOKING
        else:
            message = 'How many People'
            bot.message.reply_text(message)
            return self.PEOPLE

    def delete_booking(self, bot, update):
        response = bot.message.text
        if response == 'YES':
            logger.info(f'DELETE: {self.user_id} requested delete booking')
            user_active = self.fb.db.child(f'users/{self.fb_id}/active').get().val()
            if user_active['is_booker'] == 1:
                if 'friends' in user_active.keys():
                    friends = user_active['friends']
                    for k, v in friends.items():
                        self.fb.db.child(f'users/{k}/active').remove()
                self.fb.db.child(f'users/{self.fb_id}/active').remove()
            else:
                booker = user_active['booker']
                booker_active = self.fb.db.child(f'users/{booker}/active').get().val()
                if 'friends' in booker_active.keys():
                    for k, v in booker_active['friends'].items():
                        self.fb.db.child(f'users/{k}/active').remove()
                self.fb.db.child(f'users/{booker}/active').remove()
            restaurant = self.fb.db.child(f'restaurants/{self.restaurant_key}').get().val()
            bookings = restaurant['bookings']
            token = restaurant['details']['token_order']
            for k, v in bookings.items():
                if v['bot_id'] == self.user_id:
                    for t in v['table_id']:
                        self.sender.send(f'{token}_item:table:{t}', {'reserved': False}, 'attributes')
                    self.fb.db.child(f'restaurants/{self.restaurant_key}/bookings/{k}').remove()
            self.fb.db.child(f'restaurants/{self.restaurant_key}/customers/{self.user_id}').remove()
            message = 'Your booking has been canceled. See you soon.'
            bot.message.reply_text(message)
        else:
            message = 'Start again the bot if tou want to continue'
            bot.message.reply_text(message)

            return self.START_RETURN

    def time_booking_creation(self, slot, time_booking):
        n = len(slot)
        for i in range(n // 3 + 1):
            if i * 3 + 3 < n:
                new = slot[i * 3:i * 3 + 3]
                time_booking.append(new)
            else:
                new = slot[i * 3:]
                time_booking.append(new)

        return time_booking

    def people(self, bot, update):
        logger.info(f'BOOK: {self.user_id} sent: {bot.message.text}')
        self.people = int(bot.message.text)
        message = 'Let us now know the time. Select form the keyboard'
        try:
            time_booking = []
            dinner_slots = self.fb.db.child(f'restaurants/{self.restaurant_key}/details/dinner-slot').get().val()
            lunch_slots = self.fb.db.child(f'restaurants/{self.restaurant_key}/details/lunch-slot').get().val()
            if dinner_slots is not None:
                time_booking = self.time_booking_creation(dinner_slots, time_booking)
            if lunch_slots is not None:
                time_booking = self.time_booking_creation(lunch_slots, time_booking)
            logger.info(f'BOOK: {self.user_id} time.\nReturn Restaurant\'s available timetables: {time_booking}')
        except:
            traceback.print_exc()
            time_booking = self.time_booking
        reply_markup = ReplyKeyboardMarkup(time_booking, one_time_keyboard=True, resize_keyboard=True)
        bot.message.reply_text(message, reply_markup=reply_markup)

        return self.TIME

    def key_creation(self, user, restaurant):
        import hashlib
        m = hashlib.md5()
        s = f'{user}-{restaurant}'
        m.update(s.encode('utf-8'))
        uid = str(int(m.hexdigest(), 16))[:8]
        return uid

    def time(self, bot, update):
        logger.info(f'BOOK: {self.user_id} sent: {bot.message.text}')
        self.time_selected = bot.message.text
        u = self.fb.db.child(f'users/{self.fb_id}').get().val()
        if 'nickname' in u['details'].keys():
            nick = u['details']['nickname']
        else:
            nick = u['details']['name']
        self.join_key = self.key_creation(nick, self.restaurant_name)
        is_booked = self.post_booking()
        if is_booked:
            logger.info(f'BOOK: booking accepted')
            message = f'Booking has been accepted.\n' \
                      f'User {self.user_id} at {self.restaurant_name} for {self.people} at {self.time_selected}.\n'
            bot.message.reply_text(message)
            message = f'Share this key to your friends to let them join your table: {self.join_key}'
            bot.message.reply_text(message)
            return self.START_RETURN
        else:
            logger.info(f'BOOK: booking not available')
            message = 'Sorry there are no available tables for that many people at that time.' \
                      '\nPlease retry another time.'
            bot.message.reply_text(message)
            return self.START_RETURN

    def check_table(self, key):
        users = self.fb.download('users')
        for k, v in users.items():
            try:
                if v['active']['join_key'] == key:
                    return k, v
            except:
                pass
        return [None, None]

    def join_table(self, user_key, restaurant_key):
        self.fb.db.child('users').child(user_key).child('active').child('friends').update({self.fb_id: self.user_id})
        self.fb.db.child('users').child(self.fb_id).child('active').set({
            'restaurant_key': restaurant_key,
            'is_booker': 0,
            'booker': user_key
        })

    def join(self, bot, update):
        sent_key = bot.message.text
        key, obj = self.check_table(sent_key)
        if key is not None:
            self.join_table(key, obj['active']['restaurant_key'])
            message = f"Joined {obj['details']['name']}'s Table"
        else:
            message = 'No key has been found. Please check your key.'

        bot.message.reply_text(message)

    def post_booking(self):
        # add new booking KEY to restaurant's bookings
        is_booked = self.fb.upload_booking(self.fb_id, self.restaurant_key,
                                           self.time_selected, self.people, self.user_id)
        if is_booked:
            # add new customer to restaurant's customers
            obj = {
                'people': self.people,
                'time': self.time_selected,
                'firebase_key': self.fb_id,
                'booking_key': self.fb.hash_creator(self.user_id, self.time_selected, self.people)
            }
            self.fb.db.child('restaurants').child(self.restaurant_key).child('customers').child(self.user_id).set(obj)
            obj_active = {
                'restaurant_key': self.restaurant_key,
                'details': obj,
                'is_booker': 1,
                'join_key': self.join_key
            }
            # self.fb.db.child('users').child(self.fb_id).update({'table_key': self.table_key})

            # add new booking to user's active
            self.fb.db.child('users').child(self.fb_id).child('active').update(obj_active)
            logger.info(f'BOOK: booking completed.\nNew active customer for {self.restaurant_key} with data: {obj}\n'
                        f'New active booking for {self.user_id} with data: {obj_active} '
                        f'and table key: {self.join_key}')
            return True
        else:
            logger.info('BOOK: booking NOT completed')
            return False

    def search_user_restaurant(self):
        users = self.fb.db.child('users').get().val()
        for k, u in users.items():
            try:
                if self.user_id == u['details']['bot_id']:
                    return u['active']['restaurant_key']
            except:
                print('Web User')

    def feedback(self, bot, update):
        logger.info(f'FEEDBACK: {self.user_id} sent: {bot.message.text}')
        feeling = bot.message.text
        if feeling == 'Raise':
            feeling = 1
        elif feeling == 'Lower':
            feeling = -1
        else:
            feeling = 0

        restaurant_key = self.fb.db.child('users').child(self.fb_id).child('active').child('restaurant_key').get().val()
        if restaurant_key is None:
            message = 'You are not booked in any restaurant'
            bot.message.reply_text(message)
            return self.START_RETURN

        token = self.fb.db.child('restaurants').child(restaurant_key).child('details').child(
            'token_telemetry').get().val()
        payload = {'temperature_feedback': feeling}
        self.sender.send(f'{token}_business:1', payload, 'telemetry')
        bot.message.reply_text('Thanks for the feedback')
        logger.info(f'FEED: {self.user_id} sent {payload} to telemetry/{token}_business:1')
        return self.START_RETURN

    def checkout(self):
        restaurant = self.search_user_restaurant()
        order_obj = self.fb.db.child('orders').child(self.fb_id).child(restaurant).get().val()
        last_order = list(order_obj.keys())[-1]
        last_order = order_obj[last_order]

        # remove from thingsboard reservation table
        token = self.fb.db.child(f'restaurants/{restaurant}/details/token_order').get().val()
        tables = self.fb.db.child(f'users/{self.fb_id}/active/table_id').get().val()
        for t in tables:
            self.sender.send(f'{token}_item:table:{t}', {'reserved': False}, 'attributes')

        self.fb.db.child('restaurants').child(restaurant).child('customers').child(self.user_id).remove()
        # remove from user active bookings
        self.fb.db.child('users').child(self.fb_id).child('active').remove()
        self.fb.db.child('users').child(self.fb_id).child('last_basket').remove()
        logger.info(f'CHECKOUT: removed from {self.user_id} the active object.\nRemoved from thingsboard'
                    f'reservation.\nRemoved from Firebase Restaurant\'s active customer')

        return last_order, last_order['total']

    def others(self, bot, update):
        others = """
            /start: Restart Bot from the Beginning\n
            /sensor: Check information about the Temperature, Humidity... if you are booked to a Restaurant\n
            /ask: Ask for help to an Human Being\n
            
        """
        bot.message.reply_text(others)
        return self.START_RETURN

    def help_(self):
        print('AAA')

    def main(self):
        APP_URL = f'{self.heroku_link.replace("$APP_NAME", self.app_name)}' + self.token
        updater = Updater(self.token, use_context=True)
        self.updater = updater
        # Get the dispatcher to register handlers:
        dp = updater.dispatcher
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                self.CHECK_SIGN: [MessageHandler(Filters.text, self.check_sign)],
                self.START_RETURN: [MessageHandler(Filters.text, self.start_return)],
                self.EMAIL: [MessageHandler(self.email_filter, self.email)],
                self.NICK: [MessageHandler(Filters.text, self.nickname)],
                self.PASSWORD: [MessageHandler(Filters.text, self.password)],
                self.PASSWORD_2: [MessageHandler(Filters.text, self.password_2)],
                self.COND_1: [MessageHandler(self.keyboard_filter, self.cond1)],
                self.CHECK_BOOKING: [MessageHandler(self.key_restaurant_filter, self.check_booking)],
                self.DELETE_BOOKING: [MessageHandler(Filters.text, self.delete_booking)],
                self.PEOPLE: [MessageHandler(self.people_filter, self.people)],
                self.TIME: [MessageHandler(Filters.text, self.time)],
                self.FEED: [MessageHandler(Filters.text, self.feedback)],
                self.JOIN: [MessageHandler(Filters.text, self.join)]

            },
            fallbacks=[CommandHandler('help', self.help_)],
            allow_reentry=True
        )

        dp.add_handler(conv_handler)
        # dp.add_handler(CommandHandler('book', self.book_))
        # updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=self.token)
        # updater.bot.set_webhook(APP_URL)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    sr = TelegramBot()
    sr.main()
