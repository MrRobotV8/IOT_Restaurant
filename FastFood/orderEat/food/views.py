from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
import pyrebase
import json
from collections import OrderedDict
from pprint import pprint
from .models import*
from datetime import date

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

#TODO: REMOVE PANEL SELECTOR FROM HERE! ADD A NEW APP CALLED INDEX AS THE FIRST APP to launch or authentication app. 
def panelSelector(request):
    return render(request, 'food/zero.html')

def signIn(request):
    return render(request, 'food/login.html')

def postsign(request): #homepage
    email=request.POST.get('email')
    passw = request.POST.get('pass')
    try:
        user = authe.sign_in_with_email_and_password(email, passw)
    except:
        message = "invalid credentials"
        ctx = {'message': message}
        return render(request, "food/login.html", ctx)

    email = user['email']
    session_id = user['idToken']
    # Creating two session variable to identify the sessionid and the user's email 
    request.session['uid'] = str(session_id) 
    request.session['user'] = str(email) # Maybe it's better to use the localID to identify the user. 
    idtoken = request.session['uid']
    user_id = authe.get_account_info(idtoken)
    user_id = user_id['users'][0]['localId']
    print(request.session.items())
    #TODO: REFACTOR THE FOLLOWING LINES USING THE DICTIONARY
    all_restaurants=database.child('restaurants').get()
    rest_names=[]
    for restaurant in all_restaurants.each():
        print(type(restaurant))
        rest_names.append((restaurant.val()['details']['name']))

    name = database.child('users').child(user_id).child('details').child('name').get().val()
    ctx={'email':email,
        'rnames': rest_names,
        'user': name,
    }
    return render(request, 'food/index.html', ctx)

def signUp(request):
    #TODO: UPGRADE SIGNUP TEMPLATE
    return render(request, 'food/signUp.html')

def postsignup(request):

    name = request.POST.get('name')
    email = request.POST.get('email')
    passw = request.POST.get('psw')
    re_passw = request.POST.get('psw-repeat')
    added=0
    if passw == re_passw:
        try:
            user = authe.create_user_with_email_and_password(email, passw)
            added=1
        except:
            msg = "Unable to create account, try again"  #weak password
            return render(request, 'food/signUp.html', {'msg': msg})
    else:
        msg = "The passwords don’t match, please try again" # password matching
        return render(request, 'food/signUp.html', {'msg': msg})
    if added==1:
        uid = user['localId']
        #TODO: ADD EMAIL information
        data = {"name":name, "status":"1"}
        database.child("users").child(uid).child("details").set(data)
        #TODO: aggiungere instance del customer sul django model Customer ? 

    return render(request, 'food/signIn.html')

def logout(request):
    idtoken = request.session['uid']
    user_id = authe.get_account_info(idtoken)
    user_id = user_id['users'][0]['localId']
    try:
        database.child('users').child(user_id).child('last_basket').remove()
        del request.session['uid']
        request.session.flush()
        #Azzera Basket 
        database.child('users').child(user_id).child('last_basket').remove()
        print(request.session.items())
    except KeyError:
        pass
    message = "You are logged out!"
    ctx = {
        'message': message
    }
    return render(request, 'food/login.html', ctx)
 

def index(request):
    #TODO: WORK ON TEMPLATE INDEX.HTML
    idtoken = request.session['uid']
    user_id = authe.get_account_info(idtoken)
    user_id = user_id['users'][0]['localId']
    name = database.child('users').child(user_id).child('details').child('name').get().val()
    context={
        'user':name,
    }
    return render(request, 'food/index.html', context)   

def restaurants(request):
    
    idtoken = request.session['uid']
    user_id = authe.get_account_info(idtoken)
    user_id = user_id['users'][0]['localId']

    all_restaurants=database.child('restaurants').get()
    rest_list = {}
    description = "ristorante stellato"
    for restaurant in all_restaurants.each():
        rest_list[restaurant.key()]={'name': restaurant.val()['details']['name'], 'description': restaurant.val()['details']['description']}


    name = database.child('users').child(user_id).child('details').child('name').get().val()

    ctx={'user': name,
        'rest_list': rest_list,    
    }
    return render(request, 'food/restaurants.html', ctx)


def store(request, rest_id): #change name in menu

    #selected = request.POST.get('selection') # IS it possibile to do that without POST/GET method? like session or other things 
    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    #Update variable session to idetify the restaurant selected
    request.session['rest_id'] = str(rest_id)
    idtoken = request.session['uid']
    user_id = authe.get_account_info(idtoken)
    user_id = user_id['users'][0]['localId']
    rest_id = str(rest_id)
    name = database.child('users').child(user_id).child('details').child('name').get().val() # 

    #Azzera Basket 
    database.child('users').child(user_id).child('last_basket').remove()
    
         
    context = {
        'data':data,
        'user':name,
        'rest_id': rest_id
        }

    return render(request, 'food/menu.html', context)

    
def add_to_cart(request, rest_id, pk):

    #rest_id = request.session['rest_id']
    idtoken = request.session['uid']
    user_id = authe.get_account_info(idtoken)
    user_id = user_id['users'][0]['localId']
    product = database.child('restaurants').child(rest_id).child('menu').child(pk).get()
    quantity = request.POST.get('quantity')
    price = request.POST.get('price')
    increase = float(quantity) * float(price)
    basket_item = {str(product.key()):{'item':product.val()['name'], 'quantity': quantity, 'price':price}}
    database.child('users').child(user_id).child('last_basket').update(basket_item)
    total = database.child('users').child(user_id).child('last_basket').child('total').get().val()

    # TODO: FOR FUNCTIONALITY TO COUNT THE TOTAL_AMOUNT

    
    if total is None:
        database.child('users').child(user_id).child('last_basket').child('total').set(increase)
    else:
        actual = database.child('users').child(user_id).child('last_basket').child('total').get().val()
        total = float(actual) + increase
        database.child('users').child(user_id).child('last_basket').child('total').set(total)
        



    message = "You added " + str(quantity) + " of " + str(product.val()['name'])
    
    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    name = database.child('users').child(user_id).child('details').child('name').get().val() # 
    basket_list = dict(database.child('users').child(user_id).child('last_basket').get().val())
    total = database.child('users').child(user_id).child('last_basket').child('total').get().val()
    pprint(basket_list)
    context = {
        'data':data,
        'b_list': basket_list,
        'user':name, 
        'message': message,
        'rest_id': rest_id,
        'tot':total
        }

    return render(request, 'food/menu.html', context)
        
def remove_from_cart(request, rest_id, pk):
    idtoken = request.session['uid']
    rest_id = str(rest_id)
    user_id = authe.get_account_info(idtoken)
    user_id = user_id['users'][0]['localId']

    try:
        to_delete = database.child('users').child(user_id).child('last_basket').child(pk).get().val()
        print("To delete \n\n")
        print(to_delete)
        database.child('users').child(user_id).child('last_basket').child(pk).remove()
        message = "You deleted all the " + str(to_delete['item'])

    except:
        message = "You have tried to delete a product: the item is already deleted from your cart, check in the bottom cart section"
    
    
    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    name = database.child('users').child(user_id).child('details').child('name').get().val()
    
    total = database.child('users').child(user_id).child('last_basket').child('total').get().val() # 
    basket_list = database.child('users').child(user_id).child('last_basket').get()


    #total = sum([value for value in basket_list.values()['price']])
    print (total)
        


    context = {
        'data':data,
        'b_list': basket_list,
        'user':name, 
        'message': message,
        'rest_id': rest_id,
        'tot':total
    }

    return render(request, 'food/menu.html', context)




#TODO: DEFINE ORDER VIEW
