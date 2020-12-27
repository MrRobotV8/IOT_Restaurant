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
import paho.mqtt.client as mqtt

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


firebase = pyrebase.initialize_app(config)

database = firebase.database()
authe = firebase.auth()
#storage = firebase.storage()

categories = ['starter', 'pizza', 'burger', 'maindish', 'dessert', 'drinks']


def signIn(request):

    return render(request, 'rpanel/signIn.html')


def postSignIn(request):
    email = request.POST.get('email')
    passw = request.POST.get('pass')
    try:
        user = authe.sign_in_with_email_and_password(email, passw)
    except:
        message = 'invalid credentials'
        return render(request, 'rpanel/signIn.html', {"messg":message})

    session_id = user['idToken']
    request.session['uid'] = str(session_id)
    rest_id = user['localId']

    restaurant = database.child('restaurants').child(rest_id).get().val()
    name = database.child("restaurants").child(rest_id).child('details').child('name').get().val()
    
    try:
        data = database.child('restaurants').child(rest_id).child('menu').get().val()
        ctx = {
        'data' : data, 
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
    



def logout(request):
    
    try:
        idtoken = request.session['uid']
        rest_id = authe.get_account_info(idtoken)
        rest_id = rest_id['users'][0]['localId']
        del request.session['uid']
        request.session.flush()
        #Azzera Basket 
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
    added=0
    if passw == re_passw:
        try:
            user = authe.create_user_with_email_and_password(email, passw)
            added=1
        except:
            msg = "Unable to create account, try again"  #weak password
            print('except 1')
            return render(request, 'rpanel/register.html', {'messg': msg})
    else:
        msg = "The passwords don’t match, please try again" # password matching
        print('except 2')
        return render(request, 'rpanel/register.html', {'msg': msg})
    uid = user['localId']
    if added == 1:
        data = {"name":name, "status":"1", "address": address, "description": description, "seats":seats, 'phone':phone, 'tables':{'2':tfor2, '4':tfor4, '6':tfor6}, 'lunch-slot':list_slot_l, 'dinner-slot':list_slot_d}
        database.child("restaurants").child(uid).child("details").set(data) # idtoken
        print("here")
    else:
        msg = "Something goes wrong, try again"
        print("except 3")
        return render(request, 'rpanel/register.html', {'messg': msg})
    # TO DO: 
    '''
    mqtt 
    pub = Publisher(clientID=self.user_id, topic=topic)
    pub.publish(data)
    # topic potrebbe essere chiaveid/tables 
    '''
    #mqtt.Client(self.client, clean_session=False)

    return render(request, 'rpanel/signIn.html')
  
def menu(request): 
    idtoken = request.session['uid']
    rest_id = authe.get_account_info(idtoken)
    rest_id = rest_id['users'][0]['localId']
    name = database.child("restaurants").child(rest_id).child('details').child('name').get().val()

    return render(request, "rpanel/menu.html", {'uid': rest_id, 'name':name})

def postmenu(request):
    
    #TODO: SEARCH FUNCTION
    if request.method == 'GET' and "csrfmiddlewaretoken" in request.GET:
        search = request.GET.get('search')
        search = search.lower()
        uid = request.GET.get('uid')
        print(search)
        print(uid)
        timestamps = database.child("restaurants").child(uid).child('menu').shallow().get().val()
        names=[]
        for i in timestamps:
            nam = database.child('restaurants').child(uid).child('menu').child(i).child('name').get().val()
            names.append(nam)
        matching = [str(string) for string in names if search in string.lower()]
        print(matching)
        return HttpResponse("got it")   

    else:
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
            'description' : item_description,
            'price': item_price,
            'available': item_availability, 
            'url': item_url,
        }


        database.child('restaurants').child(rest_id).child('menu').child(millis).set(data)
        name = database.child("restaurants").child(rest_id).child('details').child('name').get().val()
        return render(request, 'rpanel/menu.html', {"name": name, "uid":rest_id, })


def home(request):
    #We need to access the exact id in the database
    idtoken = request.session['uid']
    rest_id = authe.get_account_info(idtoken)
    rest_id = rest_id['users'][0]['localId']
   
    #TODO: COPY MENU CODE FROM FOOD, IT IS SHORTER!!!! 
    '''
    timestamps = database.child("restaurants").child(rest_id).child('menu').shallow().get().val()
    name = database.child("restaurants").child(rest_id).child('details').child('name').get().val()
   
    #Converting  the timestamps dictionary into a list   
    lis_time=[]
    for i in timestamps:

        lis_time.append(i)
    lis_time.sort(reverse=True) # sorted list by addition time

    names=[]
    descriptions=[]
    prices=[]
    sections=[]
    dates=[]
    imgs=[]
    
   # This is too slow! change approach --> use json 

    for i in lis_time:
        nam = database.child('restaurants').child(rest_id).child('menu').child(i).child('name').get().val()
        des = database.child('restaurants').child(rest_id).child('menu').child(i).child('description').get().val()
        pri = database.child('restaurants').child(rest_id).child('menu').child(i).child('price').get().val()
        sec = database.child('restaurants').child(rest_id).child('menu').child(i).child('section').get().val()
        img = database.child('restaurants').child(rest_id).child('menu').child(i).child('url').get().val()
        i = float(i)
        dat = datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%Y')
        dates.append(dat)
        names.append(nam)
        descriptions.append(des)
        prices.append(pri)
        sections.append(sec)
        imgs.append(img)


    
    obj = database.child('restaurants').child(rest_id).child('menu').get()
    print('obj: ' + str(obj))
    print('type: ' + str(type(obj)))
    for o in obj.each(): 
        print(o.val())
 
    
    comb_lis = zip(dates, names, descriptions, prices, sections, imgs)

    '''
    data = database.child('restaurants').child(rest_id).child('menu').get().val()
    name = database.child("restaurants").child(rest_id).child('details').child('name').get().val()


    ctx={
        'name': name,
        #'comb_lis': comb_lis,
        #'data': sorted(obj.val().items()),
        #'data': obj.val().items(),
        'data': data,
    }
        
    

    return render (request, 'rpanel/home.html', ctx)

def profile(request):
    return render(request, "rpanel/profile.html")
"""
def create(request):

    return render(request, 'create.html')

def post_create(request):

    import time
    import datetime
    from datetime import datetime, timezone
    import pytz

    tz = pytz.timezone('Asia/Kolkata')
    time_now = datetime.now(timezone.utc).astimezone(tz)
    millis = int(time.mktime(time_now.timetuple()))

    work = request.POST.get('work')
    progress = request.POST.get('progress')
    url = request.POST.get('url')

    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']


    data = {
        'work': work,
        'progress': progress,
        'url' : url
    }

    database.child('users').child(a).child('reports').child(millis).set(data)
    name = database.child('users').child(a).child('details').child('name').get().val()

    return render(request, 'welcome.html', {"email": name})

def check(request):

    import time
    import datetime
    from datetime import timezone

    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    timeStamps = database.child('users').child(a).child('reports').shallow().get().val()
    lis_time = []

    for time in timeStamps:
        lis_time.append(time)

    lis_time.sort(reverse=True)

    work = []

    for time in lis_time:
        work.append(database.child('users').child(a).child('reports').child(time).child('work').get().val())

    date = []
    for i in lis_time:
        i = float(i)
        dat = datetime.datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%Y')
        date.append(dat)



    comb_lis = zip(lis_time, date, work)

    name = database.child('users').child(a).child('details').child('name').get().val()
    return render(request, 'check.html', {'comb_lis':comb_lis, 'email':name})

def post_check(request):
    import datetime

    time = request.GET.get('z')
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    work = database.child('users').child(a).child('reports').child(time).child('work').get().val()
    progress = database.child('users').child(a).child('reports').child(time).child('progress').get().val()
    img_url = database.child('users').child(a).child('reports').child(time).child('url').get().val()

    i = float(time)
    dat = datetime.datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%Y')

    name = database.child('users').child(a).child('details').child('name').get().val()
"""
def index(request):

    return render(request, 'rpanel/index.html')
