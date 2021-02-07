"Commited with CiccioRefactoring"
import time
import json
import datetime
from datetime import datetime, timezone
import traceback
from collections import OrderedDict
from thingsboard.main import ThingsDash


def password_checker(psw1, psw2):
    #It is possible to add filter on password security
    if psw1 == psw2:
        return True
    else:
        return False


def mapping_orders(orders, database, rest_id):
    my_orders={}
    for customer, value in orders.items():
        for rest, val in value.items():
            if rest == rest_id:
                for ts, order in val.items():
                    #print(customer)
                    #print(rest)
                    #print(ts)
                    d = datetime(
                        day=int(ts[:2]),
                        month=int(ts[2:4]),
                        year=int(ts[4:8]),
                        hour=int(ts[8:10]),
                        minute=int(ts[10:12]),
                        second=int(ts[12:14]),
                    )
                    timestamp = datetime.timestamp(d)
                    #print(d)
                    #print(timestamp)
                    my_orders[timestamp] = {
                        'name': database.child('users').child(customer).child('details').child('name').get().val(),
                        'order': order,  #dict
                        'day': d,
                        'ts': ts,
                        'customer_id': customer,
                        'status': database.child('orders').child(customer).child(rest_id).child(ts).child('order_status').get().val(),

                    }
    return my_orders


#Mapping customer orders and ordering
def mapping_customer_orders(orders, database):
    #print("Dentro")
    if orders != None:
        my_orders = {}
        #print("Not None")
        for rest, values in orders.items():
            for ts, order in values.items():
                #print(rest)
                #print(ts)
                d = datetime(
                    day=int(ts[:2]),
                    month=int(ts[2:4]),
                    year=int(ts[4:8]),
                    hour=int(ts[8:10]),
                    minute=int(ts[10:12]),
                    second=int(ts[12:14]),
                    )
                timestamp = datetime.timestamp(d)
                #print(d)
                #print(timestamp)
                my_orders[timestamp]={
                    'rest_name': database.child('restaurants').child(rest).child('details').child('name').get().val(),
                    'ts': d,
                    'order': order,
                }

        my_orders = OrderedDict(sorted(my_orders.items(),key=lambda x:x[0], reverse=True))
    else:
        #print("None")
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
    #pprint(dict_)
    ord_lst = []
    clients = list(dict_.keys())
    for cl in clients:
        orders = list(dict_[cl].keys())
        [ord_lst.append((x, cl)) for x in orders]
        ord_lst = sorted(ord_lst)

    new_dict = OrderedDict()
    # ord_lst = sorted(ord_lst, reverse=True)
    for e in ord_lst[::-1]:
        #print([e[1]], [e[0]])
        new_dict.update({e[1]: {e[0]: dict_[e[1]][e[0]]}})
    return dict(new_dict)


def cart(flag, request, database, idtoken, rest_id, pk):

    if "add" in flag:
        product = database.child('restaurants').child(rest_id).child('menu').child(pk).get()
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        increase = float(quantity) * float(price)
        basket_item = {str(product.key()): {'item': product.val()['name'], 'quantity': int(quantity), 'price': price,
                                            'url': product.val()['url']}}
        try:
            prev = database.child('users').child(idtoken).child('last_basket').child(product.key()).child('quantity').get()
            basket_item[str(product.key())]['quantity'] += int(prev.val())
            pass
        except:
            traceback.print_exc()
            pass
        database.child('users').child(idtoken).child('last_basket').update(basket_item)
        total = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
        if total is None:
            database.child('users').child(idtoken).child('last_basket').child('total').set(increase)
        else:
            actual = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
            total = float(actual) + increase
            database.child('users').child(idtoken).child('last_basket').child('total').set(total)

        message = "You added " + str(quantity) + " of " + str(product.val()['name'])
        data = database.child('restaurants').child(rest_id).child('menu').get().val()
        name = database.child('users').child(idtoken).child('details/name').get().val()  #
        basket_list = dict(database.child('users').child(idtoken).child('last_basket').get().val())
        total = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
        #print("add equal")
        
        if "telegram" in flag:

            rest_name = database.child('restaurants').child(rest_id).child('details/name').get().val()
            # pprint(basket_list)
            context = {
                'data': data,
                'b_list': basket_list,
                'user': name,
                'message': message,
                'rest_id': rest_id,
                'rest_name': rest_name,
                'idtoken': idtoken,
                'tot': total
            }
            print("telegram add")
        else:
            context = {
                'data': data,
                'b_list': basket_list,
                'user': name,
                'message': message,
                'rest_id': rest_id,
                'tot': total
            }
            print("django add")
    else: #remove
        try:
            actual = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
            to_delete = database.child('users').child(idtoken).child('last_basket').child(pk).get().val()
            price = float(database.child('users').child(idtoken).child('last_basket').child(pk).child('price').get().val())
            quantity = float(database.child('users').child(idtoken).child('last_basket').child(pk).child('quantity').get().val())
            decrease = price * quantity
            database.child('users').child(idtoken).child('last_basket').child(pk).remove()
            total = float(actual) - decrease
            database.child('users').child(idtoken).child('last_basket').child('total').set(total)
            message = "You deleted all the " + str(to_delete['item'])

        except:
            message = "You have tried to delete a product: the item is already deleted from your cart, check in the bottom cart section"

        data = database.child('restaurants').child(rest_id).child('menu').get().val()
        name = database.child('users').child(idtoken).child('details/name').get().val()

        total = database.child('users').child(idtoken).child('last_basket').child('total').get().val()  #
        basket_list = dict(database.child('users').child(idtoken).child('last_basket').get().val())
        #print("remove both")
        
        if "telegram" in flag:

            rest_name = database.child('restaurants').child(rest_id).child('details/name').get().val()
            context = {
                'data': data,
                'b_list': basket_list,
                'user': name,
                'message': message,
                'rest_id': rest_id,
                'rest_name': rest_name,
                'idtoken': idtoken,
                'tot': total
            }
            print("remove telegram")
        else:
            context = {
                'data': data,
                'b_list': basket_list,
                'user': name,
                'message': message,
                'rest_id': rest_id,
                'tot': total
            }
            print("remove django")

    return context