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
from functions import *

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
    rest_name = database.child('restaurants').child(rest_id).child('details/name').get().val()
    idtoken = request.session['uid']
    rest_id = str(rest_id)
    name = database.child('users').child(idtoken).child('details/name').get().val()  #

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

    context = cart("add telegram", request, database, idtoken, rest_id, pk)

    return render(request, 'menu_tg/menu.html', context)


def remove_from_cart(request, idtoken, rest_id, pk):

    context = cart("remove telegram", request, database, idtoken, rest_id, pk)

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

    client_name = database.child('users').child(idtoken).child('details/name').get().val()
    context = {
        'message':message,
        'client_name':client_name,
        'rest_id': rest_id,
        'idtoken': idtoken,
        }
    return render(request, 'menu_tg/checkout.html', context)


""" DEPRECATED - Future works """
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
    rest_name = database.child('restaurants').child(rest_id).child('details/name').get().val()
    name = database.child('users').child(idtoken).child('details/name').get().val()  #

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