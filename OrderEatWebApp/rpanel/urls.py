"""
Here it is defined the restaurant panel url pattern 
"""
from django.urls import path

from . import views

app_name='rpanel'  # Restaurant_panel

urlpatterns = [
    #path('index/', views.index, name='index'), DEPRECATED
    path('signin/', views.signIn, name = 'Signin'),
    path('postSignIn/', views.postSignIn, name = 'Postsignin'),
    path('logout/', views.logout, name = 'log'),
    path('signUp/', views.signUp, name = 'Signup'),
    path('postSignUp/', views.postSignUp, name = 'Postsignup'),
    path('menu/', views.menu, name="menu"),
    path('postmenu/', views.postmenu, name="postmenu"),
    path('removefrommenu/<str:pk>', views.removefrommenu, name="removefrommenu"),
    path('home/', views.home, name='home'),
    #path('profile/', views.profile, name='profile'),  DEPRECATED
    path('orders/', views.orders, name='orders'),
    path('orders/updatestatus/<str:cust>/<str:pk>', views.updatestatus, name="updatestatus"),
]
