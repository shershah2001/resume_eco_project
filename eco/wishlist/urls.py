from django.urls import path
from . import views


urlpatterns = [
    path("",views.wishlistProduct,name="wishlistproduct"),
    path('toggle/<int:id>/',views.wishlistView,name="wishlist"),

]
