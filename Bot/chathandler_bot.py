import traceback
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import ConversationHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import json
import os
from multiprocessing import Process
from functions import *
from BotFilters import *
from Firebase import Firebase
import datetime
from FeedbackSender import Sender

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))


class SmartRestaurant:
    def __init__(self):
        self.fb = Firebase()
        self.sender = Sender()
        self.fb.authenticate()
        self.restaurants = self.fb.download('restaurants')
        self.restaurants_names = [r['details']['name'] for r in self.restaurants.values()]
        self.restaurants_mapper = {self.restaurants_names[i]: list(self.restaurants.keys())[i]
                                   for i in range(len(self.restaurants_names))}

        self.initial_keyboard = [['Book', 'Order', 'Feedback'], ['Join', 'CheckOut', 'Info']]
        self.time_booking = [['19:00', '19:30', '20:00'], ['20:30', '21:00', '21:30']]

        self.email_filter = EmailFilter()
        self.keyboard_filter = KeyboardFilter()
        self.people_filter = PeopleFilter()
        self.key_restaurant_filter = KeyRestaurantFilter(self.restaurants_names)

        n_states = 17
        self.START, self.START_RETURN, self.COND_1, self.EMAIL, self.PASSWORD, \
        self.PASSWORD_2, self.NICK, self.SIGN_IN, self.CHECK_SIGN, self.CHECK_BOOKING, \
        self.ORDER, self.FEED, self.JOIN, self.CHECK, \
        self.PEOPLE, self.TIME, self.INFO = range(n_states)
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
        logger.info(f'Bot Started - {self.user_id}')
        if self.check_signin():
            if self.fb.db.child('users').child('active').child('restaurant_key').get():
                self.restaurant_key = self.fb.db.child('users').child('active').child('restaurant_key').get().val()
            message = 'Welcome back. Please select one of the following.'
            reply_markup = ReplyKeyboardMarkup(self.initial_keyboard, one_time_keyboard=True, resize_keyboard=True)
            bot.message.reply_text(message, reply_markup=reply_markup)
            return self.COND_1
        else:
            message = 'Welcome to the StartRestaurantBot. Create an account or insert credentials ' \
                      'if you already have one'
            reply_markup = ReplyKeyboardMarkup([['Create Account', 'Sign-In']], one_time_keyboard=True,
                                               resize_keyboard=True)
            bot.message.reply_text(message, reply_markup=reply_markup)

            return self.CHECK_SIGN
        # message = 'Welcome back. Please select one of the following.'
        # reply_markup = ReplyKeyboardMarkup(self.initial_keyboard, one_time_keyboard=True, resize_keyboard=True)
        # bot.message.reply_text(message, reply_markup=reply_markup)
        # return self.COND_1

    def check_sign(self, bot, update):
        if bot.message.text == 'Create Account':
            self.new = True
            bot.message.reply_text('Please Inert your email')
            return self.EMAIL
        else:
            self.new = False
            bot.message.reply_text('Insert your email')
            return self.EMAIL

    def email(self, bot, update):
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
        self.nickname = bot.message.text
        message = 'Insert now your password'
        bot.message.reply_text(message)

        return self.PASSWORD

    def password(self, bot, update):
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
        if bot.message.text == self.password:
            self.sign_up()
            message = 'You have been signed-up!'
            bot.message.reply_text(message)

            return self.START_RETURN
        else:
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
            'timestamp': int(datetime.datetime.now().timestamp())
        }
        logger.info(f'Singed-Up: {data}')

        self.fb.db.child('users').child(uid).child('details').set(data)

    def return_user(self, key, value):
        users = self.fb.download('users')
        for k, v in users.items():
            try:
                if v['details'][key] == value:
                    return v
            except:
                pass

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
        selection = bot.message.text
        if selection == 'Book':
            message = 'At which Restaurant do you want to book a table?'
            bot.message.reply_text(message)
            sorted_restaurants = sorted(self.restaurants_names)
            for i in sorted_restaurants:
                new_restaurant = i
                bot.message.reply_text(new_restaurant)
            return self.CHECK_BOOKING

        elif selection == 'Order':
            if self.fb.db.child('users').child(self.fb_id).child('active').get().val() is not None:
                restaurant = self.fb.db.child('users').child(self.fb_id).child(
                    'active').child('restaurant_key').get().val()
                message = 'Click on the link to begin the ordering phase'
                link = f'https://order-eat2021-django.herokuapp.com/tg-menu/{self.fb_id}/{restaurant}'
                self.link = link
                bot.message.reply_text(message)
                sent_link = bot.message.reply_text(link)
                # delete_callback(self.updater.bot, sent_link.message_id, sent_link.chat.id,
                #                                     ttl=3)
                # run_process(self.updater.bot, sent_link.message_id, sent_link.chat.id,
                #                                     ttl=5)

                return self.START_RETURN
            else:
                traceback.print_exc()
                message = 'You do not have any active bookings. First create a booking'
                bot.message.reply_text(message)
                return self.START_RETURN

        elif selection == 'Feedback':
            message = 'Tap if you want to change the room_temperature'
            reply_markup = ReplyKeyboardMarkup([['Lower', 'Raise', 'Good']], one_time_keyboard=True,
                                               resize_keyboard=True)
            bot.message.reply_text(message, reply_markup=reply_markup)
            return self.FEED

        elif selection == 'Join':
            message = 'You chose to JOIN a Table. Please insert the relative KEY'
            bot.message.reply_text(message)
            return self.JOIN

        elif selection == 'Wait':
            if self.fb.db.child('orders').child(self.restaurant_key).child(self.fb_id).get():
                customers_before = self.fb.db.child('restaurants').child(self.restaurant_key).child('customers').get()
                customers_before = len(customers_before.val())
                message = f'We have {customers_before} before you! Your order will be starting in ~ ' \
                          f'{customers_before / 10} Minutes'
                bot.message.reply_text(message)

                return self.START_RETURN

            else:
                message = 'You do not have placed an order yet. Please select ORDER from the keyboard menu'
                bot.message.reply_text(message)

                return self.START_RETURN

        elif selection == 'CheckOut':
            history_order, check = self.checkout()
            message = f'Your History Order: {history_order}\nYour Total: {check}\nThanks and return soon!'
            bot.message.reply_text(message)

            return self.CHECK
        elif selection == 'Info':
            restaurant = self.fb.db.child(f'users/{self.fb_id}/active/restaurant_key').get().val()
            if restaurant is not None:
                token = self.fb.db.child(f'restaurants/{restaurant}/details/token_order').get().val()
                response = self.sender.get_device_telemetry(token)
                json_response = json.loads(response.text)
                message = f'TEMPERATURE: {json_response["temperature"][-1]["value"]}°C\n' \
                          f'HUMIDITY: {json_response["humidity"][-1]["value"]}%\n' \
                          f'NOISE: {json_response["noise"][-1]["value"]}dB'
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
        restaurant_chosen = bot.message.text
        self.restaurant_name = restaurant_chosen
        restaurant_key = self.restaurants_mapper[restaurant_chosen]
        try:
            restaurant_ids = self.restaurants[restaurant_key]['customers'].keys()
            if self.user_id in list(restaurant_ids):
                message = f'You already have a Booking at {restaurant_chosen}. Do you want to change it?'
                reply_markup = ReplyKeyboardMarkup([['YES', 'NO']], one_time_keyboard=True, resize_keyboard=True)
                bot.message.reply_text(message, reply_markup=reply_markup)
            else:
                self.restaurant_key = restaurant_key
                message = 'How many People'
                bot.message.reply_text(message)
                return self.PEOPLE
        except:
            self.restaurant_key = restaurant_key
            message = 'How many People'
            bot.message.reply_text(message)
            return self.PEOPLE

    def people(self, bot, update):
        self.people = int(bot.message.text)
        message = 'Let us now know the time. Select form the keyboard'
        try:
            dinner_slots = self.fb.db.child('restaurants').child(self.restaurant_key).child(
                'details').child('dinner-slot')
            dinner_slots = dinner_slots.get().val()
            n = len(dinner_slots)
            time_booking = []
            for i in range(n // 3 + 1):
                if i * 3 + 3 < n:
                    new = dinner_slots[i * 3:i * 3 + 3]
                    time_booking.append(new)
                else:
                    new = dinner_slots[i * 3:]
                    time_booking.append(new)
        except:
            traceback.print_exc()
            time_booking = self.time_booking
        reply_markup = ReplyKeyboardMarkup(time_booking, one_time_keyboard=True, resize_keyboard=True)
        bot.message.reply_text(message, reply_markup=reply_markup)

        return self.TIME

    def key_creation(self, user, restaurant):
        s = f'{user}_{restaurant}'
        return s

    def time(self, bot, update):
        self.time_selected = bot.message.text
        u = self.return_user('bot_id', self.user_id)
        if 'nickname' in u['details'].keys():
            nick = u['details']['nickname']
        else:
            nick = u['details']['name']
        self.table_key = self.key_creation(nick, self.restaurant_name)
        message = 'This Key will be needed if anyone wants to join your table: Share it with your friends!'
        bot.message.reply_text(message)
        message = f'{self.table_key}'
        bot.message.reply_text(message)
        self.post_booking()

        return self.START_RETURN

    def check_table(self, key):
        users = self.fb.download('users')
        for k, v in users.items():
            try:
                if v['active']['table_key'] == key:
                    return k, v
            except:
                pass
        return [None, None]

    def join_table(self, user_key, restaurant_key):
        self.fb.db.child('users').child(user_key).child('active').child('friends').update({self.fb_id: self.user_id})
        self.fb.db.child('users').child(self.fb_id).child('active').set({
            'restaurant_key': restaurant_key
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
        # add new customer to restaurant's customers
        obj = {
            'people': self.people,
            'time': self.time_selected,
            'firebase_key': self.fb_id,
        }
        logger.info(f'Set {self.restaurant_key} Active customer: {obj}')
        self.fb.db.child('restaurants').child(self.restaurant_key).child('customers').child(self.user_id).set(obj)
        obj_active = {
            'restaurant_key': self.restaurant_key,
            'details': obj
        }
        logger.info(f'Set {self.fb_id} object: {obj_active}')
        self.fb.db.child('users').child(self.fb_id).update({'table_key': self.table_key})

        # add new booking to user's active
        self.fb.db.child('users').child(self.fb_id).child('active').set(obj_active)

        # add new booking KEY to restaurant's bookings
        self.fb.upload_booking(self.fb_id, self.restaurant_key, self.time_selected, self.people, self.user_id)

    def search_user_restaurant(self):
        users = self.fb.db.child('users').get().val()
        for k, u in users.items():
            try:
                if self.user_id == u['details']['bot_id']:
                    return u['active']['restaurant_key']
            except:
                print('Web User')

    def feedback(self, bot, update):
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
        logger.info(f'Send to restaurant feedback: {payload}')
        self.sender.send(f'{token}_business:1', payload, 'telemetry')
        bot.message.reply_text('Thanks for the feedback')
        return self.START_RETURN

    def checkout(self):
        restaurant = self.search_user_restaurant()
        # get bill
        # get order history
        # TODO: check date of order how to handle it
        order_obj = self.fb.db.child('orders').child(self.fb_id).child(restaurant).get().val()
        last_order = list(order_obj.keys())[-1]
        last_order = order_obj[last_order]
        # total = last_order['total']
        # last_order_history = {v.pop('url', None) for k, v in last_order.pop('total', None)}
        # add to restaurant history
        # remove from active customers of restaurant
        restaurant_obj = self.fb.db.child('restaurants').child(restaurant).child('customers').child(self.user_id).get()
        restaurant_obj = restaurant_obj.val()

        # add to user history
        history_object = {
            'restaurant': restaurant,
            'details': {
                'people': restaurant_obj['people'],
                'time': restaurant_obj['time'],
                'order': last_order,
                # 'total': total
            }
        }
        self.fb.db.child('users').child(self.fb_id).child('history').update(history_object)

        # remove from thingsboard reservation table
        token = self.fb.db.child(f'restaurants/{restaurant}/details/token_order').get().val()
        tables = self.fb.db.child(f'users/{self.fb_id}/active/table_id').get().val()
        for i, t in tables.items():
            self.sender.send(f'{token}_item:table:{t}', {'reserved': False}, 'attributes')

        self.fb.db.child('restaurants').child(restaurant).child('customers').child(self.user_id).remove()
        # remove from user active bookings
        self.fb.db.child('users').child(self.fb_id).child('active').remove()
        # remove table key
        self.fb.db.child('users').child(self.fb_id).child('table_key').remove()
        logger.info(f'Remove order from user; Remove user from restaurant customers; '
                    f'Add to user history; Return order object: {history_object}')
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
        TOKEN = '892866853:AAF3W2Dns7-Koiayk-2fuDgIDiFCfrLEfLw'
        APP_NAME = 'order-eat2021'
        APP_URL = f'https://{APP_NAME}.herokuapp.com/' + TOKEN
        updater = Updater(TOKEN, use_context=True)
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
                self.PEOPLE: [MessageHandler(self.people_filter, self.people)],
                self.TIME: [MessageHandler(Filters.text, self.time)],
                self.FEED: [MessageHandler(Filters.text, self.feedback)],
                self.JOIN: [MessageHandler(Filters.text, self.join)]

            },
            fallbacks=[CommandHandler('help', self.help_),
                       # CommandHandler('cancel', self.cancel)
                       ],
            allow_reentry=True
        )

        dp.add_handler(conv_handler)
        # dp.add_handler(CommandHandler('book', self.book_))
        # updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
        # updater.bot.set_webhook(APP_URL)
        updater.start_polling()
        updater.idle()


# def run_process(bot, message_id, chat_id, ttl):
#     p = Process(target=delete_callback(bot, message_id, chat_id, ttl))
#     p.start()
#
#
# def delete_callback(bot, message_id, chat_id, ttl=5):
#     time.sleep(ttl)
#     bot.delete_message(chat_id=chat_id, message_id=message_id)


if __name__ == '__main__':
    print('STARTED')
    sr = SmartRestaurant()
    # p1 = Process(target=sr.main)
    # p1.start()
    sr.main()