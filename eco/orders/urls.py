from django.urls import path
from orders  import views


urlpatterns = [
    path("placeorder/",views.PlaceOrder,name="placeorder"),
    path('verify_payment/',views.verify_payment,name="verify_payment"),
    path('cancelorder/',views.cancelorder,name="cancelorder"),
    path('myorders/',views.myorders,name='myorders'),
    path('orderdetails/',views.orderdetail,name='orderdetail')
]
