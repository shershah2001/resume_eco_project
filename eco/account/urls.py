from django.urls import path
from account import views

urlpatterns = [
    path('register/',views.registerView,name="register"),
    path('login/',views.userlogin,name='login'),
    path('home/',views.home,name='home'),
]
