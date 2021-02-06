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
from thingsboard.main import ThingsDash #TODO: Comment
import os
from .Dash import Dash
from functions import *


with open('../catalog.json', 'r') as f:
    config_db = json.loads(f.read())['firebase']

#FIREBASE INITIALIZATION
firebase = pyrebase.initialize_app(config_db)
authe = firebase.auth()
database = firebase.database()


#storage = firebase.storage() --> Developed in HTML

"""
GENERAL GUIDELINES:
Each function is a view or an action for the customer panel;
The try & except is used to detect if the action requested by the user is available or not
i.e the user logouts and then try to go back
messg: negative message
message: positive message
Functions: 
    signIn
    postSignIn
    logout
    signUp
    postSignUp
    menu
    postmenu
    removefrommenu
    home
    orders
    updatestatus
"""

categories = ['starter', 'pizza', 'burger', 'maindish', 'dessert', 'drinks']

"""
LOGIN PAGE RESTAURANT PANEL
success-->"GET /rpanel/signin/ HTTP/1.1" 200
input form:
    email
    password
"""
def signIn(request):
    return render(request, 'rpanel/signIn.html')

'''
POST LOGIN REQUEST:
The restaurant owner authenticates with email and password
At this point we create session variable:
    [uid] --> uid  (it's the ID Token)

'''
def postSignIn(request):
    try:
        email = request.POST.get('email')
        passw = request.POST.get('pass')
        try:
            user = authe.sign_in_with_email_and_password(email, passw)
        except:
            message = 'Invalid credentials'
            return render(request, 'rpanel/signIn.html', {"messg": message})

        session_id = user['idToken']
        request.session['uid'] = str(session_id)
        rest_id = user['localId']
        restaurant = database.child('restaurants').child(rest_id).get().val()
        name = database.child("restaurants").child(rest_id).child('details/name').get().val()
        thingsboard_url = database.child('restaurants').child(rest_id).child('details/thingsboard').get().val()

        # IF RESTAURANT HAS MENU RETURNS home.html, OTHERWISE RETURN index.html
        try:
            data = database.child('restaurants').child(rest_id).child('menu').get().val()  #MENÙ
            ctx = {
                'data': data,
                'name': name,
                'thingsboard_url': thingsboard_url,
            }
            #print("TRY \n")
            return render(request, 'rpanel/home.html', ctx)
        except:
            ctx = {
                'name': name,
                }
            #print("Excpet \n")
            return render(request, 'rpanel/index.html', ctx)
    except:
        msg = "Probably you have tried to go back, after been logged out! Plase login again!"
        ctx = {
            'messg': msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)


def logout(request):
    try:
        #idtoken = request.session['uid']
        rest_id = authe.get_account_info(request.session['uid'])
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

"""
REGISTER PAGE RESTAURANT
success--> "GET /rpanel/register/ HTTP/1.1" 200
Complex Input form, with multiple sections
"""
def signUp(request):
    return render(request, 'rpanel/register.html')

"""
POST REGISTER REQUEST
Check if password and re_password are equal:
If True: 
    Create_user by pyrebase
    Write restaurant in realtime database:
    "name": name, 
    "status": "1", 
    "address": address, 
    "description": description, 
    "seats": seats,
    'phone': phone,
    'tables': {'2': tfor2, '4': tfor4, '6': tfor6},
    'lunch-slot': list_slot_l,
    'dinner-slot': list_slot_d}
    
"""
def postSignUp(request):
    name = request.POST.get('name')  # name restaurant
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
    print("checking password")
    if password_checker(passw, re_passw)==True:
        try:
            user = authe.create_user_with_email_and_password(email, passw)
            uid = user['localId'] 
            data = {
                "name": name,
                "status": "1",
                "address": address,
                "description": description,
                "seats": seats,
                'phone': phone,
                'tables': {'2': tfor2, '4': tfor4, '6': tfor6},
                'lunch-slot': list_slot_l,
                'dinner-slot': list_slot_d,
                }
            database.child("restaurants").child(uid).child("details").set(data) 
            print("Restaurant Added!")
        except:
            msg = "Unable to create account, try again"  # weak password
            print(msg)
            return render(request, 'rpanel/register.html', {'messg': msg})
    else:
        msg = "The passwords don’t match, please try again"  # password matching
        print(msg)
        return render(request, 'rpanel/register.html', {'msg': msg})

    config = {
        'email': email,
        'uid': uid,        
    }
    config.update(data)
    dash = Dash(config)
    things = dash.create_dash()
    #TOKEN_TELEMETRY/TOKEN_ORDER/DASHBOARD_URL
    database.child('restaurants').child(uid).child('details').update(things)
   
    msg = "Account Created!"
    ctx = {
        'message': msg,
    }

    return render(request, 'rpanel/signIn.html', ctx)


def menu(request):
    try:
        rest_id = authe.get_account_info(request.session['uid'])
        rest_id = rest_id['users'][0]['localId']
        name = database.child("restaurants").child(rest_id).child('details/name').get().val()
        try:
            menu = dict(database.child('restaurants').child(rest_id).child('menu').get().val())
            pprint(menu)
        except:
            menu=None
        thingsboard_url = database.child('restaurants').child(rest_id).child('details/thingsboard').get().val()

        return render(request, "rpanel/menu.html", {'uid': rest_id, 'name': name, 'menu': menu, 'thingsboard_url': thingsboard_url})

    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg': msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)


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

        rest_id = authe.get_account_info(request.session['uid'])
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
        name = database.child("restaurants").child(rest_id).child('details/name').get().val()
        message = "Product Added!"
        menu = dict(database.child('restaurants').child(rest_id).child('menu').get().val())
        thingsboard_url = database.child('restaurants').child(rest_id).child('details/thingsboard').get().val()
        return render(request, 'rpanel/menu.html', {"name": name, "uid": rest_id, 'menu': menu, "message": message, "thingsboard_url":thingsboard_url})
    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg': msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)


def removefrommenu(request, pk):
    try:
        rest_id = authe.get_account_info(request.session['uid'])
        rest_id = rest_id['users'][0]['localId']

        database.child('restaurants').child(rest_id).child('menu').child(pk).remove()
        name = database.child("restaurants").child(rest_id).child('details/name').get().val()
        message = "Product Deleted!"
        menu = database.child('restaurants').child(rest_id).child('menu').get().val()
        thingsboard_url = database.child('restaurants').child(rest_id).child('details/thingsboard').get().val()

        context = {
            "name": name,
            "uid": rest_id,
            'menu': menu,
            "message": message,
            "thingsboard_url": thingsboard_url
        }

        return render(request, 'rpanel/menu.html', context)
    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg': msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)


def home(request):
    try:
        rest_id = authe.get_account_info(request.session['uid'])
        rest_id = rest_id['users'][0]['localId']

        data = database.child('restaurants').child(rest_id).child('menu').get().val()
        name = database.child("restaurants").child(rest_id).child('details/name').get().val()
        thingsboard_url = database.child('restaurants').child(rest_id).child('details/thingsboard').get().val()


        ctx = {
            'name': name,
            'data': data,
            "thingsboard_url":thingsboard_url,
        }

        return render(request, 'rpanel/home.html', ctx)
    except:
        msg = "Something goes wrong! Try again :)"
        ctx = {
            'messg': msg
        }
        return render(request, 'food/signIn.html', ctx)


def orders(request): 
    rest_id = authe.get_account_info(request.session['uid'])
    rest_id = rest_id['users'][0]['localId']

    orders = database.child('orders').get().val()
    my_orders = mapping_orders(orders, database, rest_id)
    my_orders = OrderedDict(sorted(my_orders.items(), key=lambda x: x[0], reverse=True))

    info = dict(database.child("restaurants").child(rest_id).child('details').get().val())
    thingsboard_url = database.child('restaurants').child(rest_id).child('details/thingsboard').get().val()
    name = database.child("restaurants").child(rest_id).child('details/name').get().val()


    context = {
        'name': name,
        'my_orders': my_orders,
        'info': info,
        'thingsboard_url':thingsboard_url,
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

#TODO: RICARICA PAGINA --> MSG
def updatestatus(request, cust, pk):
    order_status = request.POST.get('orderstatus')
    idtoken = request.session['uid']
    rest_id = authe.get_account_info(idtoken)
    rest_id = rest_id['users'][0]['localId']

    database.child('orders').child(cust).child(rest_id).child(pk).child('order_status').set(order_status)  # or update?

    orders = database.child('orders').get().val()
    my_orders = mapping_orders(orders, database, rest_id)

    my_orders = OrderedDict(sorted(my_orders.items(), key=lambda x: x[0], reverse=True))

    info = dict(database.child("restaurants").child(rest_id).child('details').get().val())
    thingsboard_url = database.child('restaurants').child(rest_id).child('details/thingsboard').get().val()
    name = database.child("restaurants").child(rest_id).child('details/name').get().val()

    context = {
        'name': name,
        'my_orders': my_orders,
        'info': info,
        'thingsboard_url': thingsboard_url,
    }
    return render(request, "rpanel/orders.html", context)

""" DEPRECATED   -FUTURE WORKS
def profile(request):
    try:
        idtoken = request.session['uid']
        rest_id = authe.get_account_info(idtoken)
        rest_id = rest_id['users'][0]['localId']
        info = dict(database.child("restaurants").child(
            rest_id).child('details').get().val())

        return render(request, "rpanel/profile.html", {'info': info})
    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg': msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)
"""