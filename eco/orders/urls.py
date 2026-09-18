from django.urls import path
from orders  import views

print("ORDERS URLS LOADED")
urlpatterns = [
    path("placeorder/",views.PlaceOrder,name="placeorder"),
    path('verify_payment/',views.verify_payment,name="verify_payment"),
    path('cancelorder/',views.cancelorder,name="cancelorder"),
    path('allorders/',views.all_orders,name='allorders'),
    path('myorders/',views.myorders,name='myorders'),
    path("orderdetails/",views.orderdetail,name="orderdetail"),
    path('razorpay_webhook/',views.razorpay_webhook,name="razorpay_webhook")
]
