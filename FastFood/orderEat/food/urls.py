from django.urls import path

from . import views

app_name = 'food'

urlpatterns = [
    path('pizza/', views.pizza, name='pizzas'),
    path('index/', views.index, name='index'), #with the / it doesn't work properly
    path('signin/', views.signIn, name='signin'),
    path('postsign/', views.postsign, name='postsign'),
    path('logout/', views.logout, name='log'),
    path('signup/', views.signUp, name='signup'),
    path('postsignup/', views.postsignup, name='postsignup'),
]