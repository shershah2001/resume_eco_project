from django.urls import path
from carts import views

urlpatterns = [
    path("",views.cartView,name="cart"),
    path("add_to_cart/<slug:product_slug>/",views.add_to_cart,name="add_to_cart"),
    path('remove_to_cart/<slug:product_slug>/',views.remove_to_cart,name="remove_to_cart"),
    path('increase/<slug:product_slug>/',views.increaseView,name="increase"),
    path('decrease/<slug:product_slugs>/',views.decreaseView,name="decrease"),
    path('checkout/',views.checkout,name="checkout"),
]
