from django.urls import path
from carts import views

urlpatterns = [
    path("cart/",views.cartView,name="cartview"),
    path("add_to_cart/<slug:slug>/",views.add_to_cart,name="add_to_cart"),
    path('remove_to_cart/<slug:slug>/',views.remove_to_cart,name="remove_to_cart"),
    path('increase/<slug:slug>/',views.increaseView,name="increase"),
    path('decrease/<slug:slug>/',views.decreaseView,name="decrease"),
]
