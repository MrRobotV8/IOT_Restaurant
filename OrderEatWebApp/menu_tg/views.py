from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
import pyrebase
import json
from collections import OrderedDict
from pprint import pprint
from .models import *
from datetime import datetime
from django.core.mail import send_mail

with open('../catalog.json', 'r') as f:
    config = json.loads(f.read())['firebase']
##Initialize Firebase
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()



def menu(request, idtoken, rest_id):
    request.session['uid'] = str(idtoken)
    request.session['rest_id'] = str(rest_id)

    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    rest_name = database.child('restaurants').child(rest_id).child('details').child('name').get().val()
    idtoken = request.session['uid']
    rest_id = str(rest_id)
    name = database.child('users').child(idtoken).child('details').child('name').get().val()  #

    # Azzera Basket
    database.child('users').child(idtoken).child('last_basket').remove()

    context = {
        'data': data,
        'rest_name': rest_name,
        'user': name,
        'rest_id': rest_id,
        'idtoken': idtoken,

    }

    return render(request, 'menu_tg/menu.html', context)


import traceback


def add_to_cart(request, idtoken, rest_id, pk):

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
    print('Totale')
    print(total)

    if total is None:
        database.child('users').child(idtoken).child('last_basket').child('total').set(increase)
    else:
        actual = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
        total = float(actual) + increase
        database.child('users').child(idtoken).child('last_basket').child('total').set(total)

    message = "You added " + str(quantity) + " of " + str(product.val()['name'])

    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    name = database.child('users').child(idtoken).child('details').child('name').get().val()  #
    basket_list = dict(database.child('users').child(idtoken).child('last_basket').get().val())
    total = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
    rest_name = database.child('restaurants').child(rest_id).child('details').child('name').get().val()
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

    return render(request, 'menu_tg/menu.html', context)


def remove_from_cart(request, idtoken, rest_id, pk):

    try:
        actual = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
        to_delete = database.child('users').child(idtoken).child('last_basket').child(pk).get().val()
        print("To delete \n\n")
        print(to_delete)
        price = float(database.child('users').child(idtoken).child('last_basket').child(pk).child('price').get().val())
        quantity = float(
            database.child('users').child(idtoken).child('last_basket').child(pk).child('quantity').get().val())
        decrease = price * quantity
        database.child('users').child(idtoken).child('last_basket').child(pk).remove()
        total = float(actual) - decrease
        database.child('users').child(idtoken).child('last_basket').child('total').set(total)
        message = "You deleted all the " + str(to_delete['item'])

    except:
        message = "You have tried to delete a product: the item is already deleted from your cart, check in the bottom cart section"

    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    name = database.child('users').child(idtoken).child('details').child('name').get().val()

    total = database.child('users').child(idtoken).child('last_basket').child('total').get().val()  #
    basket_list = dict(database.child('users').child(idtoken).child('last_basket').get().val())
    rest_name = database.child('restaurants').child(rest_id).child('details').child('name').get().val()


    # total = sum([value for value in basket_list.values()['price']])
    print(total)

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

    return render(request, 'menu_tg/menu.html', context)

def checkout(request, idtoken, rest_id):
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")

    try:
        last_basket = database.child('users').child(idtoken).child('last_basket').get().val()
        last_basket['order_status'] = "ACCEPTED"
        last_basket['is_bot'] = 1
        database.child('orders').child(idtoken).child(rest_id).child(dt_string).set(last_basket)
        message = "Your order has been accepted by OrderEat"
    except:
        message = "Something goes wrong, please try again"

    client_name = database.child('users').child(idtoken).child('details').child('name').get().val()
    context = {
        'message':message,
        'client_name':client_name,
        'rest_id': rest_id,
        'idtoken': idtoken,
        }
    return render(request, 'menu_tg/checkout.html', context)

""" DEPRECATED - future works """
'''
def contacts(request, idtoken, rest_id):
    fname = request.POST.get('fname')
    mail = request.POST.get('mail')
    obj = str(request.POST.get('people')) + str(request.POST.get('date'))
    message = request.POST.get('message') # this is a good way to use the code already written to send email from the EMAIL_HOST defined in settings. 
    message = message + "\n\nRemember to answer to %s" %fname + " at %s" %mail
    mailTo= ['ciccio.guaiana@gmail.com'] # orderat@gmail.com
    print(mailTo)
    print(message )
    

    # send an email 
    send_mail(
        obj,   # what is usually called OGGETTO / molti lo chiamo subject
        message , #message - The real message of the mail with our processing to understand who is writing
        mail, # EMAIL_HOST_USER in settings.py
        mailTo,  #recipient LIST 
    )

    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    rest_name = database.child('restaurants').child(rest_id).child('details').child('name').get().val()
    name = database.child('users').child(idtoken).child('details').child('name').get().val()  #

    # Azzera Basket
    database.child('users').child(idtoken).child('last_basket').remove()

    context = {
        'data': data,
        'rest_name': rest_name,
        'user': name,
        'rest_id': rest_id,
        'idtoken': idtoken,

    }

    return render(request, 'menu_tg/menu.html', context)
'''