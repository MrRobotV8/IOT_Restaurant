from django.urls import path

from . import views

app_name = 'food'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('restaurants/', views.restaurants, name='restaurants'),
    path('menu/', views.menu, name='menu'),
    path('signin/', views.signIn, name='signin'),
    path('postsign/', views.postsign, name='postsign'),
    path('logout/', views.logout, name='log'),
    path('signup/', views.signUp, name='signup'),
    path('postsignup/', views.postsignup, name='postsignup'),
]