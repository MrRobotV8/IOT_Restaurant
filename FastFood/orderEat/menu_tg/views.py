from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
import pyrebase
import json
from collections import OrderedDict
from pprint import pprint
from .models import*


#Please Note the difference between auth from django.contrib and the variable authe=firebase.auth()
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

##Initialize Firebase
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()
#firebase.analytics()

def menu(request, idtoken, rest_id): 

    request.session['uid']=str(idtoken)
    request.session['rest_id']=str(rest_id)

    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    rest_name = database.child('restaurants').child(rest_id).child('details').child('name').get().val()
    idtoken = request.session['uid']
    rest_id = str(rest_id)
    name = database.child('users').child(idtoken).child('details').child('name').get().val() # 

    #Azzera Basket 
    database.child('users').child(idtoken).child('last_basket').remove()
    
         
    context = {
        'data':data,
        'rest_name': rest_name,
        'user':name,
        'rest_id': rest_id,
        'idtoken':idtoken,

        }

    return render(request, 'menu_tg/menu.html', context)

    
def add_to_cart(request, idtoken, rest_id, pk):

    #rest_id = request.session['rest_id']
    #idtoken = request.session['uid']
    #user_id = authe.get_account_info(idtoken)
    #user_id = user_id['users'][0]['localId']
    product = database.child('restaurants').child(rest_id).child('menu').child(pk).get()
    quantity = request.POST.get('quantity')
    price = request.POST.get('price')
    increase = float(quantity) * float(price)
    basket_item = {str(product.key()):{'item':product.val()['name'], 'quantity': quantity, 'price':price, 'url':product.val()['url']}}
    database.child('users').child(idtoken).child('last_basket').update(basket_item)
    basket_items = database.child('users').child(idtoken).child('last_basket').get()
    
    total = database.child('users').child(idtoken).child('last_basket').child('total').get().val()

    # TODO: FOR FUNCTIONALITY TO COUNT THE TOTAL_AMOUNt
    
    if total is None:
        database.child('users').child(idtoken).child('last_basket').child('total').set(increase)
    else:
        actual = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
        total = float(actual) + increase
        database.child('users').child(idtoken).child('last_basket').child('total').set(total)
    


    message = "You added " + str(quantity) + " of " + str(product.val()['name'])
    
    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    name = database.child('users').child(idtoken).child('details').child('name').get().val() # 
    basket_list = dict(database.child('users').child(idtoken).child('last_basket').get().val())
    total = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
    pprint(basket_list)
    context = {
        'data':data,
        'b_list': basket_list,
        'user':name, 
        'message': message,
        'rest_id': rest_id,
        'idtoken': idtoken,
        'tot': total
        }

    return render(request, 'menu_tg/menu.html', context)
        
def remove_from_cart(request, idtoken, rest_id, pk):
    #idtoken = request.session['uid']
    #rest_id = str(rest_id)
    #user_id = authe.get_account_info(idtoken)
    #user_id = user_id['users'][0]['localId']

    try:
        actual = database.child('users').child(idtoken).child('last_basket').child('total').get().val()
        to_delete = database.child('users').child(idtoken).child('last_basket').child(pk).get().val()
        print("To delete \n\n")
        print(to_delete)
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
    name = database.child('users').child(idtoken).child('details').child('name').get().val()
    
    total = database.child('users').child(idtoken).child('last_basket').child('total').get().val() # 
    basket_list = dict(database.child('users').child(idtoken).child('last_basket').get().val())


    #total = sum([value for value in basket_list.values()['price']])
    print (total)
        


    context = {
        'data':data,
        'b_list': basket_list,
        'user':name, 
        'message': message,
        'rest_id': rest_id,
        'idtoken': idtoken,
        'tot':total
    }

    return render(request, 'menu_tg/menu.html', context)
