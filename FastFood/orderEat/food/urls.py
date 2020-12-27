from django.urls import path, re_path

from . import views

app_name = 'food'

urlpatterns = [
    path('signin/', views.signIn, name='signin'),
    path('postsign/', views.postsign, name='postsign'),
    path('logout/', views.logout, name='log'),
    path('signup/', views.signUp, name='signup'),
    path('postsignup/', views.postsignup, name='postsignup'),
    path('index/', views.index, name='index'),
    path('restaurants/', views.restaurants, name='restaurants'),
    #path('menu/', views.menu, name='menu'),
    path('restaurants/<str:rest_id>', views.store, name="store"),
    #path('cart/', views.cart, name="cart"),
	path('restaurants/<str:rest_id>/add/<str:pk>', views.add_to_cart, name="addtocart"),
	path('restaurants/<str:rest_id>/remove/<str:pk>', views.remove_from_cart, name="removefromcart"),

]
