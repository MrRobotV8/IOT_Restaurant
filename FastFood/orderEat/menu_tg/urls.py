from django.urls import path, re_path

from . import views

app_name = 'menu_tg'

urlpatterns = [
    path('<str:idtoken>/<str:rest_id>', views.menu, name='menu' ),
    path('<str:idtoken>/<str:rest_id>/add/<str:pk>', views.add_to_cart, name='addtocart' ),
    path('<str:idtoken>/<str:rest_id>/remove/<str:pk>', views.remove_from_cart, name='removefromcart' ),
]