from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
import pyrebase
import json
from collections import OrderedDict
from pprint import pprint

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
'''
all_restaurants=database.child('restaurants').get()
#uids=[]
#rest_names=[]
rest_list = {}

for restaurant in all_restaurants.each():
    #print(restaurant.val())
    print('\n\n')
    rest_list[restaurant.key()]=restaurant.val()['details']['name']
    #rest_names.append((restaurant.val()['details']['name']))
    #uids.append(restaurant.key())

print(rest_list)
'''
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
    session_id = user['idToken']
    request.session['uid'] = str(session_id)
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    all_restaurants=database.child('restaurants').get()
    uids=[]
    rest_names=[]
    for restaurant in all_restaurants.each():
        print(type(restaurant))
        rest_names.append((restaurant.val()['details']['name']))
        uids.append(restaurant.key())

    name = database.child('users').child(a).child('details').child('name').get().val()
    ctx={'email':email,
        'rnames': rest_names,
        'user': name,
    
    }
    return render(request, 'food/index.html', ctx)

def logout(request):
    auth.logout(request)
    return render(request, 'food/signIn.html')

def signUp(request):
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
        data = {"name":name, "status":"1"}
        database.child("users").child(uid).child("details").set(data)
    return render(request, 'food/signIn.html')

def panelSelector(request):
    return render(request, 'food/zero.html')
    
def restaurants(request):
    
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    all_restaurants=database.child('restaurants').get()
    all_restaurants_val=database.child('restaurants').get().val()
    chiavi = all_restaurants_val.keys()
    tmp = [all_restaurants_val[x]['details']['name'] for x in chiavi]
    print('TMP \n')
    pprint(tmp)
    #print('all_restaurant_val: \n')
    #pprint(dict(all_restaurants_val))

    #print('all_restaurant \n')
    #print(type(all_restaurants))
    #print('\n\n')

    rest_list = {}
    description = "ristorante stellato"
    for restaurant in all_restaurants.each():
        #print('single restaurant '+ str(type(restaurant)))
        #pprint(restaurant.val())
        rest_list[restaurant.key()]={'name': restaurant.val()['details']['name'], 'description': description}
    #print(rest_list)

    name = database.child('users').child(a).child('details').child('name').get().val()

    ctx={'user': name,
        'rest_list': rest_list,    
    }
    return render(request, 'food/restaurants.html', ctx)

def index(request):
    context={}
    return render(request, 'food/index.html', context)

def menu(request):
    selected = request.POST.get('selection') # IS it possibile to do that without POST/GET method? like session or other things 
    data = database.child('restaurants').child(selected).child('menu').get().val()
    '''
    The following code is always the same to retreive the user ifnromation, i think we should use the session to cover this issue
    '''
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    name = database.child('users').child(a).child('details').child('name').get().val() # 

    context = {'data':data,
            'user':name}
    return render(request, 'food/menu.html', context)

def cart(request):
    context = {}
    return render(request, 'food/cart.html', context)

def checkout(request):
    context={}
    return render(request, 'food/checkout.html', context)
    