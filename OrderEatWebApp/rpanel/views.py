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
from pprint import pprint

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

        try:
            data = database.child('restaurants').child(
                rest_id).child('menu').get().val()
            ctx = {
                'data': data,
                'name': name,
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
    name = request.POST.get('name')
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
    msg = "Account Created!"
    ctx = {
        'message': msg,
    }
    return render(request, 'rpanel/signIn.html', ctx)


def menu(request):
    try:
        idtoken = request.session['uid']
        rest_id = authe.get_account_info(idtoken)
        rest_id = rest_id['users'][0]['localId']
        name = database.child("restaurants").child(rest_id).child('details').child('name').get().val()
        menu = dict(database.child('restaurants').child(rest_id).child('menu').get().val())
        pprint(menu)

        return render(request, "rpanel/menu.html", {'uid': rest_id, 'name': name, 'menu':menu})
    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg' : msg,
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
    try: 
        idtoken = request.session['uid']
        rest_id = authe.get_account_info(idtoken)
        rest_id = rest_id['users'][0]['localId']
        
        orders = database.child('orders').get().val()
        users = []
        for user in orders.keys():
            users.append(user)

        my_orders = {}
        for user in users:
            if database.child('orders').child(user).child(rest_id).get():
                name = database.child('users').child(user).child('details').child('name').get().val()
                try:
                    my_orders[name] = dict(database.child('orders').child(user).child(rest_id).get().val())
                except:
                    pass
            else:
                pass
        pprint(my_orders)   
        #TODO: ordinare secondo




        info = dict(database.child("restaurants").child(rest_id).child('details').get().val())
        context ={
            'my_orders': my_orders,
            'info': info,
        }
        return render(request, "rpanel/orders.html", context)
    except:
        msg = "Session expired! Please login again!"
        ctx = {
            'messg' : msg,
        }
        return render(request, 'rpanel/signIn.html', ctx)


def updatestatus(request, id):
    return render(request, "rpanel/orders.html", context)