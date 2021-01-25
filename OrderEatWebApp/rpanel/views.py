from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
import pyrebase
import time
import datetime
from datetime import datetime, timezone
import pytz
import json
import collections
from collections import OrderedDict
from pprint import pprint
from thingsboard.main import ThingsDash
import os



# Please Note the difference between auth from django.contrib and the variable authe=firebase.auth()
# TODO BEST PRACTICE --> file config dedicato
config = {
    'apiKey': "AIzaSyCNUQyDSE8LglsRzQGpk8OJGvTj2IyicT4",
    'authDomain': "ordereat-94887.firebaseapp.com",
    'databaseURL': "https://ordereat-94887.firebaseio.com",
    'projectId': "ordereat-94887",
    'storageBucket': "ordereat-94887.appspot.com",
    'messagingSenderId': "89417842986",
    'appId': "1:89417842986:web:162875424095cecd65de53",
    'measurementId': "G-BHVSYJK293"
}


firebase = pyrebase.initialize_app(config)

database = firebase.database()
authe = firebase.auth()
#storage = firebase.storage()

categories = ['starter', 'pizza', 'burger', 'maindish', 'dessert', 'drinks']


def signIn(request):

    return render(request, 'rpanel/signIn.html')


def postSignIn(request):
    try:
        email = request.POST.get('email')
        passw = request.POST.get('pass')
        try:
            user = authe.sign_in_with_email_and_password(email, passw)
        except:
            message = 'invalid credentials'
            return render(request, 'rpanel/signIn.html', {"messg": message})

        session_id = user['idToken']
        request.session['uid'] = str(session_id)
        rest_id = user['localId']

        restaurant = database.child('restaurants').child(rest_id).get().val()
        name = database.child("restaurants").child(
            rest_id).child('details').child('name').get().val()
        thingsboard_url = database.child('restaurants').child(rest_id).child('details').child('thingsboard').get().val()

        try:
            data = database.child('restaurants').child(
                rest_id).child('menu').get().val()
            ctx = {
                'data': data,
                'name': name,
                'thingsboard_url': thingsboard_url,
            }
            print("TRY \n")
            return render(request, 'rpanel/home.html', ctx)
        except:
            ctx = {
                'name': name,
            }
            print("Excpet \n")
            return render(request, 'rpanel/index.html', ctx)
    except:
        msg = "Probably you have tried to go back, after been logged out! Plase login again!"
        ctx = {
            'messg' : msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)

def logout(request):

    try:
        idtoken = request.session['uid']
        rest_id = authe.get_account_info(idtoken)
        rest_id = rest_id['users'][0]['localId']
        del request.session['uid']
        request.session.flush()
        # Azzera Basket
        print(request.session.items())
    except KeyError:
        pass
    message = "You are logged out!"
    ctx = {
        'message': message
    }
    return render(request, 'rpanel/signIn.html', ctx)


def signUp(request):

    return render(request, 'rpanel/register.html')


def postSignUp(request):
    name = request.POST.get('name')   #name restaurant
    email = request.POST.get('email')
    passw = request.POST.get('psw')
    re_passw = request.POST.get('psw-repeat')
    description = request.POST.get('description')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    seats = request.POST.get('seats')
    tfor2 = request.POST.get('tfor2')
    tfor4 = request.POST.get('tfor4')
    tfor6 = request.POST.get('tfor6')
    list_slot_l = request.POST.getlist('slot-l')
    list_slot_d = request.POST.getlist('slot-d')

    print(list_slot_d)
    print(list_slot_l)
    added = 0
    if passw == re_passw:
        try:
            user = authe.create_user_with_email_and_password(email, passw)
            added = 1
        except:
            msg = "Unable to create account, try again"  # weak password
            print('except 1')
            return render(request, 'rpanel/register.html', {'messg': msg})
    else:
        msg = "The passwords don’t match, please try again"  # password matching
        print('except 2')
        return render(request, 'rpanel/register.html', {'msg': msg})
    uid = user['localId']
    if added == 1:
        data = {"name": name, "status": "1", "address": address, "description": description, "seats": seats, 'phone': phone,
                'tables': {'2': tfor2, '4': tfor4, '6': tfor6}, 'lunch-slot': list_slot_l, 'dinner-slot': list_slot_d}
        database.child("restaurants").child(
            uid).child("details").set(data)  # idtoken
        print("here")
    else:
        msg = "Something goes wrong, try again"
        print("except 3")
        return render(request, 'rpanel/register.html', {'messg': msg})


    # TODO: ADD VICTOR'S CODE TO CREATE ENTITY RESTAURANT
    public = True
    td = ThingsDash()
    owner_id = td.create_customer(title=email, address=address)  #customer_id
    building_name = f"{owner_id}_building:1"
    building_label = address    # Indirizzo del ristorante 
    building_id = td.create_restaurant_asset(asset_name=building_name, asset_label=building_label)
    # assign asset/building to customer
    td.relation_customer_contains_asset(owner_id, building_id)
    if public:
        td.assign_device_to_public(building_id)
    else:
        td.assign_asset_to_customer(owner_id, building_id)

    restaurant_name = f"{building_id}_business:1"
    restaurant_token = restaurant_name
    restaurant_label = name # Nome del ristorante
    restaurant_device_id = td.save_restaurant_device(device_name=restaurant_name, device_label=restaurant_label, device_token=restaurant_name)
    database.child('restaurants').child(uid).child('details').child('token').set(restaurant_device_id)
    # set restaurant attributes
    td.set_device_attributes(restaurant_token, {"customer_owner": owner_id,
     "address": address, "description": description, "name": name, "phone": phone, "seats": seats, "status":"1", "dinner_slot": "", "lunch_slot": ""})
    # assign device to asset
    td.relation_asset_contains_device(building_id, restaurant_device_id)
    # assign device to customer
    if public:
        td.assign_device_to_public(restaurant_device_id)
    else:
        td.assign_device_to_customer(owner_id, restaurant_device_id)


    # create the tables
    dict_tables = {2:int(tfor2), 4:int(tfor4), 6:int(tfor6)}  # this should be given by ciccio
    table_number = 0
    for n_seats, n_tables in dict_tables.items():
        for i in range(n_tables):
            table_number += 1
            # create device table
            table_token = f"{restaurant_device_id}_item:table:{table_number}"
            table_device_id = td.save_table_device(table_number=table_number, device_token=table_token, device_restaurant_id=restaurant_device_id)
            # set table attributes
            td.set_device_attributes(table_token, {"customer_owner": owner_id, "seats": n_seats})
            # assign device to customer
            if public:
                td.assign_device_to_public(table_device_id)
            else:
                td.assign_device_to_customer(owner_id, table_device_id)
            # assign device to asset
            td.relation_asset_contains_device(building_id, table_device_id)
            # assign device to restaurant device
            td.relation_device_contains_device(restaurant_device_id, table_device_id)

    # create the togo device
    togo_token = f"{restaurant_device_id}_togo"
    togo_device_id = td.save_togo_device(togo_token, restaurant_device_id)
    # assign device to asset
    td.relation_asset_contains_device(building_id, togo_device_id)
    #assign device to owner
    if public:
        td.assign_device_to_public(togo_device_id)
    else:
        td.assign_device_to_customer(owner_id, togo_device_id)
    # set togo attributes
    td.set_device_attributes(togo_token, {"customer_owner": owner_id})

    # creates a dashboard and assigns it to the owner
    custom_dash = td.customize_dashboard(restaurant_dashboard_path="thingsboard/restaurant_default.json", restaurant_label=restaurant_label, customer_id=owner_id)
    dashboard_id = td.save_dashboard(custom_dash)
    if public:
        # make the dashboard public and get its url
        dashboard_id, public_client_id, dashboard_url = td.assign_dashboard_to_public_customer(dashboard_id)
        print(f"Customer dashboard URL: {dashboard_url}")
    else:
        td.assign_dashboard_to_customer(owner_id, dashboard_id)

    database.child('restaurants').child(uid).child('details').child('thingsboard').set(dashboard_url)
    
    # create empty menu

    database.child('restaurants').child(uid).child('menu').set({'item': 'first'})


    


    msg = "Account Created!"
    ctx = {
        'message': msg,
    }

    return render(request, 'rpanel/signIn.html', ctx)


def menu(request):

    idtoken = request.session['uid']
    rest_id = authe.get_account_info(idtoken)
    rest_id = rest_id['users'][0]['localId']
    name = database.child("restaurants").child(rest_id).child('details').child('name').get().val()
    menu = dict(database.child('restaurants').child(rest_id).child('menu').get().val())
    pprint(menu)

    return render(request, "rpanel/menu.html", {'uid': rest_id, 'name': name, 'menu':menu})


def postmenu(request):
    try:
        tz = pytz.timezone('Europe/Rome')
        time_now = datetime.now(timezone.utc).astimezone(tz)
        millis = int(time.mktime(time_now.timetuple()))

        item_section = request.POST.get('item-section')
        item_name = request.POST.get('item-name')
        item_description = request.POST.get('item-description')
        item_price = request.POST.get('item-price')
        item_availability = request.POST.get('available')
        item_url = request.POST.get('url')

        idtoken = request.session['uid']
        rest_id = authe.get_account_info(idtoken)
        rest_id = rest_id['users'][0]['localId']

        data = {
            'name': item_name,
            'section': item_section,
            'description': item_description,
            'price': item_price,
            'available': item_availability,
            'url': item_url,
        }

        database.child('restaurants').child(rest_id).child('menu').child(millis).set(data)
        name = database.child("restaurants").child(rest_id).child('details').child('name').get().val()
        message = "Product Added!"
        menu = dict(database.child('restaurants').child(rest_id).child('menu').get().val())
        pprint(menu)
        return render(request, 'rpanel/menu.html', {"name": name, "uid": rest_id,'menu': menu, "message": message})
    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg' : msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)

def removefrommenu(request, pk):
    try:
        idtoken = request.session['uid']
        rest_id = authe.get_account_info(idtoken)
        rest_id = rest_id['users'][0]['localId']

        database.child('restaurants').child(rest_id).child('menu').child(pk).remove()
        name = database.child("restaurants").child(
                rest_id).child('details').child('name').get().val()
        message = "Product Deleted!"
        menu = database.child('restaurants').child(rest_id).child('menu').get().val()



        context = {
            "name": name, 
            "uid": rest_id,
            'menu': menu, 
            "message": message

        }

        return render(request, 'rpanel/menu.html', context )
    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg' : msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)
    
def home(request):
    try:
        # We need to access the exact id in the database
        idtoken = request.session['uid']
        rest_id = authe.get_account_info(idtoken)
        rest_id = rest_id['users'][0]['localId']

        data = database.child('restaurants').child(
            rest_id).child('menu').get().val()
        name = database.child("restaurants").child(
            rest_id).child('details').child('name').get().val()

        ctx = {
            'name': name,
            # 'comb_lis': comb_lis,
            # 'data': sorted(obj.val().items()),
            # 'data': obj.val().items(),
            'data': data,
        }

        return render(request, 'rpanel/home.html', ctx)
    except:
        msg="Something goes wrong! Try again :)"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/signIn.html', ctx)


def profile(request):
    try:
        idtoken = request.session['uid']
        rest_id = authe.get_account_info(idtoken)
        rest_id = rest_id['users'][0]['localId']
        info = dict(database.child("restaurants").child(
            rest_id).child('details').get().val())

        return render(request, "rpanel/profile.html",{'info': info})
    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg' : msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)


def index(request):
    #TODO: Delete IT!

    return render(request, 'rpanel/index.html')

def orders(request):
    
    idtoken = request.session['uid']
    rest_id = authe.get_account_info(idtoken)
    rest_id = rest_id['users'][0]['localId']
    
    orders = database.child('orders').get().val()
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
                        'name':database.child('users').child(customer).child('details').child('name').get().val(),
                        'order': order,
                        'day': d,
                        'ts':ts,
                        'customer_id': customer,
                        'status': database.child('orders').child(customer).child(rest_id).child(ts).child('order_status').get().val(),

                    }

    my_orders = OrderedDict(sorted(my_orders.items(),key=lambda x:x[0], reverse=True))

    '''
    users = []
    for user in orders.keys():
        users.append(user)

    my_orders = {}
    for user in users:
        if database.child('orders').child(user).child(rest_id).get():
            name = database.child('users').child(user).child('details').child('name').get().val()
            ts = database.child('orders').child(user).child(rest_id).get().val()
            try:
                my_orders[name] = dict(database.child('orders').child(user).child(rest_id).get().val())
            except:
                pass
        else:
            pass
    

    pprint(my_orders)   
    #TODO: ordinare secondo
    #my_orders = order_dict(my_orders)
    print('******* New dict ********\n\n')
    pprint(my_orders)
    '''






    info = dict(database.child("restaurants").child(rest_id).child('details').get().val())
    context ={
        'my_orders': my_orders,
        'info': info,
    }
    return render(request, "rpanel/orders.html", context)
'''
    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg' : msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)
'''

def updatestatus(request, cust, pk):
    order_status = request.POST.get('orderstatus')
    idtoken = request.session['uid']
    rest_id = authe.get_account_info(idtoken)
    rest_id = rest_id['users'][0]['localId']


    database.child('orders').child(cust).child(rest_id).child(pk).child('order_status').set(order_status) #or update?

    orders = database.child('orders').get().val()
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
                        'name':database.child('users').child(customer).child('details').child('name').get().val(),
                        'order': order,
                        'day': d,
                        'ts':ts,
                        'customer_id':customer,
                        'status': database.child('orders').child(cust).child(rest_id).child(pk).child('order_status').get().val(),
                    }
    
    my_orders = OrderedDict(sorted(my_orders.items(),key=lambda x:x[0], reverse=True))

    info = dict(database.child("restaurants").child(rest_id).child('details').get().val())
    context ={
        'my_orders': my_orders,
        'info': info,
    }
    return render(request, "rpanel/orders.html", context)


'''
import os



if __name__ == "__main__":
    print(os.listdir())

    # creates a dashboard and assigns it to the owner
    f = open("thingsboard/template_restaurant.json")
    
''' 

def order_dict(dict_):
    pprint(dict_)
    ord_lst = []
    clients = list(dict_.keys()) 
    for cl in clients:
        orders = list(dict_[cl].keys())
        [ord_lst.append((x,cl)) for x in orders]
        ord_lst = sorted(ord_lst)

    new_dict = OrderedDict()
    #ord_lst = sorted(ord_lst, reverse=True)
    for e in ord_lst[::-1]:
        print([e[1]],[e[0]])
        new_dict.update({e[1]:{e[0]:dict_[e[1]][e[0]]}})
    return dict(new_dict)
