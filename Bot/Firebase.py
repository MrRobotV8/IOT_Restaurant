import traceback
import logging
import pyrebase
from thingsboard.main import ThingsDash
import datetime
import copy
from FeedbackSender import Sender
import json

# Enable logging for displaying prints
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class Firebase:
    def __init__(self):
        with open('../catalog.json', 'r') as f:
            self.config = json.loads(f.read())['firebase']
        self.sender = Sender()
        self.firebase = pyrebase.initialize_app(self.config)
        self.td = ThingsDash()
        self.start_stream = True

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

    def upload_booking(self, user_firebase, restaurant_key, hour, n_people, user_id):
        # Check before uploading
        hash_key = self.hash_creator(user_id, hour, n_people)
        table_key = self.check_table_availability(restaurant_key, hash_key)
        if len(table_key) > 0:
            logger.info('TABLE: table available')
            to_set = {
                'bot_id': user_id,
                'table_id': table_key
            }
            for t in table_key:
                token = self.db.child(f'restaurants/{restaurant_key}/details/token_order').get().val()
                self.sender.send(f'{token}_item:table:{t}', {'reserved': True}, 'attributes')
            self.db.child('restaurants').child(restaurant_key).child('bookings').child(hash_key).set(to_set)
            self.db.child(f'users/{user_firebase}/active').update({'table_id': table_key})
            logger.info(f'UPLOAD BOOKING:\nRestaurant {restaurant_key} new booking')
            return True
        else:
            logger.info('TABLE: table NOT available')
            # TODO: no tables available; create new path
            print('Your booking was not uploaded')
            return False
    
    def check_table_availability(self, restaurant_key, hash_key):
        logger.info(f'TABLES: look for available table in {restaurant_key}')
        tables = self.download(f'restaurants/{restaurant_key}/details/tables')
        t_new = copy.deepcopy(tables)
        u_date, u_hour, u_people, u_user = self.unhash(hash_key)
        try:
            bookings = self.download(f'restaurants/{restaurant_key}/bookings')
            bookings_keys = bookings.keys()
            for k in bookings_keys:
                date, hour, people, user = self.unhash(k)
                if hour == u_hour:
                    p = int(people)
                    assigned, t_new = self.assign_table(p, t_new)
        except:
            print('No bookings')
        p = int(u_people)
        assigned, t_new = self.assign_table(p, t_new)
        table_key = self.assign_key_table(tables, t_new, assigned)
        if len(assigned) > 0:
            return table_key
        else:
            return []

    @staticmethod
    def assign_key_table(t_old, t_new, assigned):
        if len(assigned) == 1:
            to_add = 0
            for k, v in t_old.items():
                v = int(v)
                if k == assigned[0]:
                    break
                else:
                    to_add += v
            table_key = [int(t_old[assigned[0]]) - int(t_new[assigned[0]]) + to_add]
        elif len(assigned) > 1:
            table_key = []
            for a in assigned:
                to_add = 0
                for k, v in t_old.items():
                    v = int(v)
                    if k == a:
                        break
                    else:
                        to_add += v
                table_key.append(int(t_old[a]) - int(t_new[a]) + to_add)
        else:
            table_key = None
        return table_key

    @staticmethod
    def assign_table(people, tables):
        tables_assigned = None
        for k, v in tables.items():
            if int(v) > 0 and int(k) >= people:
                tables_assigned = [k]
                break
        if tables_assigned is None:
            for k, v in tables.items():
                for kk, vv in tables.items():
                    if (int(v) > 0) and (int(vv) > 0) and (int(kk) + int(k) >= people) and kk != k:
                        tables_assigned = [k, kk]
                        break
                    elif (int(v) > 1) and (int(vv) > 1) and (int(kk) + int(k) >= people) and kk == k:
                        tables_assigned = [k, kk]
                        break
        for t in tables_assigned:
            tables[t] = int(tables[t]) - 1

        return tables_assigned, tables

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
        return date, hour, n_people, user

    def callback_listen(self, message):
        if self.start_stream:
            pass
        else:
            try:
                event = message['event']
                if event == 'put':
                    path = message['path']
                    data = message['data']
                    path = path[1:].split('/')
                    if len(path) == 1:
                        user_key = path[0]
                        rest_key = list(data.keys())[0]
                        ts = list(data.values())[0]
                    else:
                        user_key = path[0]
                        rest_key = path[1]
                        ts = data
                    token = self.db.child(f'restaurants/{rest_key}/details/token_order').get().val()
                    user = self.db.child('users').child(user_key).get().val()
                    user_name = user['details']['name']
                    hash = user['active']['details']['booking_key']
                    table_key = self.db.child('restaurants').child(rest_key).child('bookings').child(hash).child(
                        'table_id').get().val()
                    ts.pop('address', None)
                    ts.pop('is_bot', None)
                    ts.pop('order_status', None)
                    total = f"{ts['total']} Euro"
                    ts.pop('total', None)
                    order = [f"{v['item']} x {v['quantity']}" for v in ts.values()]
                    order = ' - '.join(order)
                    payload = {"order": order, "user": user_name, 'total': total}
                    for t in table_key:
                        access_token = f"{token}_item:table:{t}"
                        self.td.create_table_order(device_access_token=access_token,
                                                   payload=payload)
            except:
                traceback.print_exc()

        self.start_stream = False

    def listener(self):
        self.stream = self.db.child('orders').stream(self.callback_listen)


if __name__ == '__main__':
    fb = Firebase()
    fb.authenticate()
    import time
    fb.listener()
    try:
        while True:
            pass
    except:
        fb.stream.close()
