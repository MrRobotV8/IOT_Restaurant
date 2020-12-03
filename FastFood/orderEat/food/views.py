from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
import pyrebase

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

all_restaurants=database.child('restaurants').get()
uids=[]
for restaurant in all_restaurants.each():
    print(type(restaurant))
    uids.append(restaurant.key())

def signIn(request):

    return render(request, 'food/signIn.html')

def postsign(request):
    email=request.POST.get('email')
    passw = request.POST.get('pass')
    try:
        user = authe.sign_in_with_email_and_password(email, passw)
    except:
        message = "invalid credentials"
        ctx = {'message': message}
        return render(request, "food/signIn.html", ctx)
    ctx={'email':email}
    session_id=user['idToken']
    request.session['uid']=str('session_id')
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
    
def index(request):
    return render(request, 'food/index.html')

def pizza(request):
    return render(request, 'food/pizza.html')
