import traceback
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
import pyrebase
import json
from collections import OrderedDict
from pprint import pprint
from .models import *
from datetime import date, datetime

# Please Note the difference between auth from django.contrib and the variable authe=firebase.auth()
#TODO: Config File!
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

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()


# firebase.analytics()

# TODO: REMOVE PANEL SELECTOR FROM HERE! ADD A NEW APP CALLED INDEX AS THE FIRST APP to launch or authentication app.
def panelSelector(request):
    return render(request, 'food/zero.html')


def signIn(request):
    return render(request, 'food/login.html')


def postsign(request):  # homepage
    try:
        email = request.POST.get('email')
        passw = request.POST.get('pass')
        try:
            user = authe.sign_in_with_email_and_password(email, passw)
        except:
            message = "invalid credentials"
            ctx = {'messg': message}
            return render(request, "food/login.html", ctx)

        email = user['email']
        session_id = user['idToken']
        # Creating two session variable to identify the sessionid and the user's email
        request.session['uid'] = str(session_id)
        # Maybe it's better to use the localID to identify the user.
        request.session['user'] = str(email)
        idtoken = request.session['uid']
        user_id = authe.get_account_info(idtoken)
        user_id = user_id['users'][0]['localId']
        request.session['user_id'] = user_id
        print(request.session.items())
        # TODO: REFACTOR THE FOLLOWING LINES USING THE DICTIONARY
        all_restaurants = database.child('restaurants').get()
        rest_names = []
        for restaurant in all_restaurants.each():
            print(type(restaurant))
            rest_names.append((restaurant.val()['details']['name']))

        name = database.child('users').child(user_id).child(
            'details').child('name').get().val()
        ctx = {'email': email,
            'rnames': rest_names,
            'user': name,
            }
        return render(request, 'food/index.html', ctx)
    except:
        msg="Something goes wrong! Probably session is expired, try again!"
        ctx = {
        'message': msg
        }
        return render(request, 'food/login.html', ctx)



def signUp(request):
    return render(request, 'food/signUp.html')


def postsignup(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    passw = request.POST.get('psw')
    re_passw = request.POST.get('psw-repeat')
    #address = request.POST.get('address')
    added = 0
    if passw == re_passw:
        try:
            user = authe.create_user_with_email_and_password(email, passw)
            added = 1
        except:
            msg = "Unable to create account, try again"  # weak password
            return render(request, 'food/signUp.html', {'msg': msg})
    else:
        msg = "The passwords don’t match, please try again"  # password matching
        return render(request, 'food/signUp.html', {'msg': msg})
    if added == 1:
        uid = user['localId']
        data = {"name": name, "email": email,
                 "is_bot": "0"}
                 #"address": address,
        database.child("users").child(uid).child("details").set(data)

    return render(request, 'food/login.html')


def logout(request):
    
    try:
        idtoken = request.session['uid']
        user_id = authe.get_account_info(idtoken)
        user_id = user_id['users'][0]['localId']
        #database.child('users').child(user_id).child('last_basket').remove()
        del request.session['uid']
        request.session.flush()
        # Azzera Basket
        #database.child('users').child(user_id).child('last_basket').remove()
        print(request.session.items())
    except KeyError:
        pass
    message = "You are logged out!"
    ctx = {
        'message': message
    }
    return render(request, 'food/login.html', ctx)


def index(request):
    try:
        user_id = request.session['user_id']
        name = database.child('users').child(user_id).child(
            'details').child('name').get().val()
        context = {
            'user': name,
        }
        return render(request, 'food/index.html', context)
    except:
        msg="Something goes wrong! Try again :)"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/login.html', ctx)


def restaurants(request):
    try:
        idtoken = request.session['uid']
        user_id = authe.get_account_info(idtoken)
        user_id = user_id['users'][0]['localId']

        all_restaurants = database.child('restaurants').get()
        rest_list = {}
        description = "ristorante stellato"
        for restaurant in all_restaurants.each():
            rest_list[restaurant.key()] = {'name': restaurant.val()['details']['name'],
                                            'description': restaurant.val()['details']['description']}

        name = database.child('users').child(user_id).child(
            'details').child('name').get().val()

        ctx = {'user': name,
                'rest_list': rest_list,
                }
        return render(request, 'food/restaurants.html', ctx)
    except:
        msg="Something goes wrong! Try again :)"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/login.html', ctx)


def store(request, rest_id):  # change name in menu
    try:
        # selected = request.POST.get('selection') # IS it possibile to do that without POST/GET method? like session or other things
        data = database.child('restaurants').child(
            rest_id).child('menu').get().val()
        # Update variable session to idetify the restaurant selected
        request.session['rest_id'] = str(rest_id)
        idtoken = request.session['uid']
        user_id = authe.get_account_info(idtoken)
        user_id = user_id['users'][0]['localId']
        rest_id = str(rest_id)
        name = database.child('users').child(user_id).child(
            'details').child('name').get().val()  #

        # Azzera Basket
        database.child('users').child(user_id).child('last_basket').remove()

        context = {
            'data': data,
            'user': name,
            'rest_id': rest_id
        }

        return render(request, 'food/menu.html', context)
    except:
        msg="Something goes wrong! Try again :)"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/login.html', ctx)


def add_to_cart(request, rest_id, pk):
    try:
        # rest_id = request.session['rest_id']
        idtoken = request.session['uid']
        user_id = authe.get_account_info(idtoken)
        user_id = user_id['users'][0]['localId']
        product = database.child('restaurants').child(rest_id).child('menu').child(pk).get()
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        increase = float(quantity) * float(price)
        basket_item = {str(product.key()): {'item': product.val()['name'], 'quantity': int(quantity), 'price': price,
                                            'url': product.val()['url']}}
        try:
            prev = database.child('users').child(user_id).child('last_basket').child(product.key()).child('quantity').get()
            basket_item[str(product.key())]['quantity'] += int(prev.val())
            pass
        except:
            traceback.print_exc()
            pass
        database.child('users').child(user_id).child('last_basket').update(basket_item)

        total = database.child('users').child(user_id).child('last_basket').child('total').get().val()

        if total is None:
            database.child('users').child(user_id).child('last_basket').child('total').set(increase)
        else:
            actual = database.child('users').child(user_id).child('last_basket').child('total').get().val()
            total = float(actual) + increase
            database.child('users').child(user_id).child('last_basket').child('total').set(total)

        message = "You added " + str(quantity) + \
            " of " + str(product.val()['name'])

        data = database.child('restaurants').child(
            rest_id).child('menu').get().val()
        name = database.child('users').child(user_id).child(
            'details').child('name').get().val()  #
        basket_list = dict(database.child('users').child(
            user_id).child('last_basket').get().val())
        total = database.child('users').child(user_id).child(
            'last_basket').child('total').get().val()
        context = {
            'data': data,
            'b_list': basket_list,
            'user': name,
            'message': message,
            'rest_id': rest_id,
            'tot': total
        }

        return render(request, 'food/menu.html', context)
    except:
        msg="Something goes wrong! Probably session is expired, try again!"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/login.html', ctx)


def remove_from_cart(request, rest_id, pk):
    try:
        idtoken = request.session['uid']
        rest_id = str(rest_id)
        user_id = authe.get_account_info(idtoken)
        user_id = user_id['users'][0]['localId']

        try:
            actual = database.child('users').child(user_id).child(
                'last_basket').child('total').get().val()
            to_delete = database.child('users').child(
                user_id).child('last_basket').child(pk).get().val()
            print("To delete \n\n")
            print(to_delete)
            price = float(database.child('users').child(user_id).child(
                'last_basket').child(pk).child('price').get().val())
            quantity = float(
                database.child('users').child(user_id).child('last_basket').child(pk).child('quantity').get().val())
            decrease = price * quantity
            database.child('users').child(user_id).child(
                'last_basket').child(pk).remove()
            total = float(actual) - decrease
            database.child('users').child(user_id).child(
                'last_basket').child('total').set(total)
            message = "You deleted all the " + str(to_delete['item'])

        except:
            message = "You have tried to delete a product: the item is already deleted from your cart, check in the bottom cart section"

        data = database.child('restaurants').child(
            rest_id).child('menu').get().val()
        name = database.child('users').child(user_id).child(
            'details').child('name').get().val()

        total = database.child('users').child(user_id).child(
            'last_basket').child('total').get().val()  #
        basket_list = dict(database.child('users').child(
            user_id).child('last_basket').get().val())

        # total = sum([value for value in basket_list.values()['price']])
        print(total)

        context = {
            'data': data,
            'b_list': basket_list,
            'user': name,
            'message': message,
            'rest_id': rest_id,
            'tot': total
        }

        return render(request, 'food/menu.html', context)
    except:
        msg="Something goes wrong! Probably session is expired, try again!"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/login.html', ctx)


def checkout(request, rest_id):
    try:
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y%H%M%S")
        idtoken = request.session['user_id']
        client_name = database.child('users').child(
            idtoken).child('details').child('name').get().val()
        #client_address = database.child('users').child(idtoken).child('details').child('address').get().val()
        client_address = request.POST.get('address')
        is_bot = False
        delivery = {
            'address': client_address,
            'is_bot': is_bot,
        }

        try:
            last_basket = database.child('users').child(
                idtoken).child('last_basket').get().val()
            database.child('orders').child(idtoken).child(
                rest_id).child(dt_string).set(last_basket)
            database.child('orders').child(
                idtoken).child(rest_id).child(dt_string).update(delivery)

            message = "Your order has been accepted by OrderEat"
        except:
            message = "Something goes wrong, please try again"

        order = dict(database.child('orders').child(
            idtoken).child(rest_id).child(dt_string).get().val())

        del order['total']
        del order['is_bot']
        del order['address']
        total = database.child('orders').child(idtoken).child(
            rest_id).child(dt_string).child('total').get().val()

        context = {
            'message': message,
            'user': client_name,
            'tot': total,
            'rest_id': rest_id,
            'idtoken': idtoken,
            'order': order,
            'address': client_address,
        }
        return render(request, 'food/checkout.html', context)
    except:
        msg="Something goes wrong! Probably session is expired, try again!"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/login.html', ctx)


def orders(request):
    try:
        user_id = request.session['user_id']
        client_name = database.child('users').child(
            user_id).child('details').child('name').get().val()
        try:

            last_order = dict(database.child('users').child(user_id).child('last_basket').get().val())
            del last_order['total']
            pprint(last_order)
            last_order_total = database.child('users').child(
                user_id).child('last_basket').child('total').get().val()
            pprint(last_order_total)
        except:
            last_order = None
            last_order_total = None

        orders = database.child('orders').child(user_id).get().val()
        pprint(orders)
        rest_keys = []
        for rest in orders.keys():
            rest_keys.append(rest)
        my_orders = {}
        for rest in rest_keys:
            rest_name = database.child('restaurants').child(rest).child('details').child('name').get().val()
            try:
                my_orders[rest_name] = dict(database.child('orders').child(user_id).child(rest).get().val())
            except:
                pass
        pprint(my_orders)

        context = {
            # 'history': history,
            'orders': my_orders,
            'user': client_name,
            'last_order': last_order,
            'tot': last_order_total,
        }

        return render(request, 'food/order.html', context)
    except:
        msg = "Something goes wrong! Please Try again :)"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/login.html', ctx)
