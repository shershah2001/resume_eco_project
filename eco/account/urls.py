from django.urls import path
from account import views
from carts.views import checkout
urlpatterns = [
    path('register/',views.registerView,name="register"),
    path('login/',views.userlogin,name='login'),
    path('userprofile/',views.userprofile,name="userprofile"),
    path('address/',views.addressView,name="address"),
    path('address/<int:id>/', views.editAddressView, name='edit_address'),
    path('address/delete/<int:id>/',views.deleteAddressView,name="delete_address"),
    path('logout/',views.userlogout,name="logout"),
]
