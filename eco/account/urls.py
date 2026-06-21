from django.urls import path
from account import views

urlpatterns = [
    path('register/',views.registerView,name="register"),
    path('login/',views.userlogin,name='login'),
    path('userprofile/',views.userprofile,name="userprofile"),
    path('address/',views.addressView,name="address"),
    path('logout/',views.userlogout,name="logout"),
]
