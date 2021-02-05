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
from thingsboard.main import ThingsDash
from .functions import *

with open('../catalog.json', 'r') as f:
    config_db = json.loads(f.read())['firebase']

# Initialize Firebase
firebase = pyrebase.initialize_app(config_db)
authe = firebase.auth()
database = firebase.database()

"""
GENERAL GUIDELINES:
Each function is a view or an action for the customer panel;
The try & except is used to detect if the action requested by the user is available or not
i.e the user logouts and then try to go back
messg: negative message
message: positive message 
"""

'''
INITIAL PAGE WHERE THE USER {REST/CUST} CAN SELECT THE PORTAL
success --> "GET / HTTP/1.1" 200
'''
def panelSelector(request):
    return render(request, 'food/zero.html')


#TODO: REFACTOR FOLDER FOOD IN CPANEL --> In any case the app food is related to the Customer Panel
"""
LOGIN PAGE CUSTOMER
success-->"GET /food/signin/ HTTP/1.1" 200
input form:
    email
    password
"""
def signIn(request):
    return render(request, 'food/login.html')

'''
POST LOGIN REQUEST:
The user authenticates with email and passw!
At this point we create  two session variable:
    [uid] --> uid  (it's the ID Token)
    [user]--> user-email
    [user_id]--> user_id 

'''
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
        request.session['uid'] = str(session_id)
        request.session['user'] = str(email)
        #idtoken = request.session['uid']
        user_id = authe.get_account_info(request.session['uid'])
        user_id = user_id['users'][0]['localId']
        request.session['user_id'] = user_id
        print(request.session.items())  #COMMENT
        name = database.child('users').child(user_id).child('details').child('name').get().val()
        ctx = {
            'user': name,
            }
        return render(request, 'food/index.html', ctx)
    except:
        msg="Something goes wrong! Probably session is expired, try again!"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/login.html', ctx)


"""
REGISTER PAGE CUSTOMER
success--> "GET /food/signup/ HTTP/1.1" 200
input form:
    NAME
    EMAIL
    PASSWORD
    REPEAT PASSWORD
"""
def signUp(request):
    return render(request, 'food/signUp.html')

"""
POST REGISTER REQUEST
Check if password and re_password are equal:
If True: 
    Create_user by pyrebase
    Write user in realtime database:
    Name;
    Mail;
    Is_Bot=0;
"""
def postsignup(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    passw = request.POST.get('psw')
    re_passw = request.POST.get('psw-repeat')
    #address = request.POST.get('address')  DEPRECATED
    added = 0
    if password_checker(passw, re_passw)==True: #True 
        try:
            user = authe.create_user_with_email_and_password(email, passw)
            added = 1
            uid = user['localId']
            data = {
                "name": name,
                "mail": email,
                "is_bot": 0,
                }
            database.child("users").child(uid).child("details").set(data)
            msg = "Account Created! Please fill the form and login"
            return render(request, 'food/login.html', {'message':msg})

        except:
            msg = "Unable to create account, try again" # Invalid Credentials
            return render(request, 'food/signUp.html', {'messg': msg})
    else:
        msg = "The passwords don’t match, please try again"  # password matching
        return render(request, 'food/signUp.html', {'messg': msg})
        

"""
LOGOUT REQUEST
Flush the session variables --> Try except in each function detect if the user can go back after been logged out
"""
def logout(request):
    
    try:
        user_id = authe.get_account_info(request.session['uid'])
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

"""
GET REQUEST FOR THE INDEX PAGE
If success --> returns the index.html 
the name is passed to populate the navigation bar
"""
def index(request):
    try:
        user_id = request.session['user_id']
        name = database.child('users').child(user_id).child('details').child('name').get().val()
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

"""
GET REQUEST FOR THE RESTAURANTS LIST
"""
def restaurants(request):
    try:
        user_id = authe.get_account_info(request.session['uid'])
        user_id = user_id['users'][0]['localId']
        all_restaurants = database.child('restaurants').get()
        rest_list = {}
        #description = "ristorante stellato" DEPRECATED
        for restaurant in all_restaurants.each():
            rest_list[restaurant.key()] = {'name': restaurant.val()['details']['name'],
                                            'description': restaurant.val()['details']['description']}

        name = database.child('users').child(user_id).child('details').child('name').get().val()

        ctx = {
            'user': name,
            'rest_list': rest_list,
            }

        return render(request, 'food/restaurants.html', ctx)

    except:
        msg="Something goes wrong! Try again :)"
        ctx = {
        'messg': msg
        }
        return render(request, 'food/login.html', ctx)

"""
GET REQUEST WITH SELECTED RESTAURANT IN THE PREVIOUS PAGE 
rest_id URI
"""
def store(request, rest_id):  
    try:
        data = database.child('restaurants').child(rest_id).child('menu').get().val()
        # Update variable session to idetify the restaurant selected
        request.session['rest_id'] = str(rest_id)
        user_id = authe.get_account_info(request.session['uid'])
        user_id = user_id['users'][0]['localId']
        rest_id = str(rest_id)
        name = database.child('users').child(user_id).child('details').child('name').get().val() 

        # When the user enters a restaurant menu page his last basket is deleted - AZZERA LAST BASKET
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

"""
The cart is implemented here with two function:
add_to_cart % remove_from_cart
POST Request
rest_id: restaurant id 
pk: id product selected
1)Update a TEMP_bakset ad user child
"""

def add_to_cart(request, rest_id, pk):
    try:
        user_id = authe.get_account_info(request.session['uid'])
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

        message = "You added " + str(quantity) + " of " + str(product.val()['name'])

        data = database.child('restaurants').child(rest_id).child('menu').get().val()
        name = database.child('users').child(user_id).child('details').child('name').get().val()  #
        basket_list = dict(database.child('users').child(user_id).child('last_basket').get().val())
        total = database.child('users').child(user_id).child('last_basket').child('total').get().val()
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
        rest_id = str(rest_id)
        user_id = request.session['user_id']


        try:
            actual = database.child('users').child(user_id).child('last_basket').child('total').get().val()
            to_delete = database.child('users').child(user_id).child('last_basket').child(pk).get().val()
            print("To delete \n\n")
            print(to_delete)
            price = float(database.child('users').child(user_id).child('last_basket').child(pk).child('price').get().val())
            quantity = float(database.child('users').child(user_id).child('last_basket').child(pk).child('quantity').get().val())
            decrease = price * quantity
            database.child('users').child(user_id).child('last_basket').child(pk).remove()
            total = float(actual) - decrease
            database.child('users').child(user_id).child('last_basket').child('total').set(total)
            message = "You deleted all the " + str(to_delete['item'])

        except:
            message = "You have tried to delete a product: the item is already deleted from your cart, check in the bottom cart section"

        data = database.child('restaurants').child(rest_id).child('menu').get().val()
        name = database.child('users').child(user_id).child('details').child('name').get().val()

        total = database.child('users').child(user_id).child('last_basket').child('total').get().val()  
        basket_list = dict(database.child('users').child(user_id).child('last_basket').get().val())

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

"""
POST request: client address (it's a delivery order)
1)Set the order in firebase with details
2)Create delivery order in Thingsboard
"""
def checkout(request, rest_id):
    try:
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y%H%M%S")
        idtoken = request.session['user_id']    #usually called user_id, maybe I was drunk
        client_name = database.child('users').child(idtoken).child('details').child('name').get().val()
        client_address = request.POST.get('address')
        is_bot = 0   #False
        delivery = {
            'address': client_address,
            'is_bot': is_bot,
        }

        try:
            last_basket = database.child('users').child(idtoken).child('last_basket').get().val()
            database.child('orders').child(idtoken).child(rest_id).child(dt_string).set(last_basket)
            database.child('orders').child(idtoken).child(rest_id).child(dt_string).update(delivery)

            message = "Your order has been accepted by OrderEat"
        except:
            message = "Something goes wrong, please try again"

        order = dict(database.child('orders').child(
            idtoken).child(rest_id).child(dt_string).get().val())

        del order['total']
        del order['is_bot']
        del order['address']
        total = database.child('orders').child(idtoken).child(rest_id).child(dt_string).child('total').get().val()
        
        order_status = "ACCEPTED"
        database.child('orders').child(idtoken).child(rest_id).child(dt_string).child('order_status').set(order_status)

        #Create delivery order on Thingsboard 
        token = database.child('restaurants').child(rest_id).child('details').child('token_order').get().val()
        togo_order(token, order, client_name, client_address)

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

"""
GET REQUEST

"""
def orders(request):
    try:
        user_id = request.session['user_id']
        client_name = database.child('users').child(user_id).child('details').child('name').get().val()
        try:

            last_order = dict(database.child('users').child(user_id).child('last_basket').get().val())
            del last_order['total']
            pprint(last_order)
            last_order_total = database.child('users').child(user_id).child('last_basket').child('total').get().val()
            pprint(last_order_total)
        except:
            last_order = None
            last_order_total = None

        orders = database.child('orders').child(user_id).get().val()
        print("orders")
        pprint(orders)
        my_orders = mapping_customer_orders(orders, database)
        context = {
            'my_orders': my_orders,
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

