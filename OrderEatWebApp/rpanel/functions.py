"Commited with CiccioRefactoring"
import time
import json
import datetime
from datetime import datetime, timezone



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

def mapping_orders(orders, database, rest_id):
    my_orders={}
    for customer, value in orders.items():
        for rest, val in value.items():
            if rest == rest_id:
                for ts, order in val.items():
                    print(customer)
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
                    my_orders[timestamp] = {
                        'name': database.child('users').child(customer).child('details').child('name').get().val(),
                        'order': order,  #dict
                        'day': d,
                        'ts': ts,
                        'customer_id': customer,
                        'status': database.child('orders').child(customer).child(rest_id).child(ts).child('order_status').get().val(),

                    }
    return my_orders