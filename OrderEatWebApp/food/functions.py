"Refactoring By Francesco"
import time
from datetime import datetime, timezone
import json
from thingsboard.main import ThingsDash
from collections import OrderedDict

def open_json(file):
    with open(file) as f:
        obj = json.loads(f.read())
    return obj


def write_json(file, obj):
    with open(file, 'w') as f:
        f.write(json.dumps(obj, indent=4))


def keys_restaurants(restaurant_obj):
    keys_names = [(k, v['name']) for k, v in restaurant_obj.items()]
    return keys_names

def password_checker(psw1, psw2):
    #It is possible to add filter on password security
    if psw1 == psw2:
        return True
    else:
        return False
#Mapping customer orders and ordering
def mapping_customer_orders(orders, database):
    print("Dentro")
    if orders != None:
        my_orders = {}
        print("Not None")
        for rest, values in orders.items():
            for ts, order in values.items():
                print(rest)
                print(ts)
                d = datetime(
                    day=int(ts[:2]),
                    month=int(ts[2:4]),
                    year=int(ts[4:8]),
                    hour=int(ts[8:10]),
                    minute=int(ts[10:12]),
                    second=int(ts[12:14]),
                    )
                timestamp = datetime.timestamp(d)
                print(d)
                print(timestamp)
                my_orders[timestamp]={
                    'rest_name': database.child('restaurants').child(rest).child('details').child('name').get().val(),
                    'ts': d,
                    'order': order,
                }

        my_orders = OrderedDict(sorted(my_orders.items(),key=lambda x:x[0], reverse=True))
    else:
        print("None")
        my_orders=None

    return my_orders

#Create delivery order on Thingsboard 
def togo_order(token, order, client_name, client_address):
    td = ThingsDash()
    togo_token = f"{token}_togo"
    x = ""
    for dish in order.values():
        x += f"{dish['item']}*{dish['quantity']}, "
    td.create_togo_order(device_access_token=togo_token, payload={"client": client_name, "order": x, "address": client_address})  

# DEPRECATED
def order_dict(dict_):
    pprint(dict_)
    ord_lst = []
    clients = list(dict_.keys())
    for cl in clients:
        orders = list(dict_[cl].keys())
        [ord_lst.append((x, cl)) for x in orders]
        ord_lst = sorted(ord_lst)

    new_dict = OrderedDict()
    # ord_lst = sorted(ord_lst, reverse=True)
    for e in ord_lst[::-1]:
        print([e[1]], [e[0]])
        new_dict.update({e[1]: {e[0]: dict_[e[1]][e[0]]}})
    return dict(new_dict)