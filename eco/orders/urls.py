from django.urls import path
from orders  import views


urlpatterns = [
    path('verify_payment/',views.verify_payment,name="verify_payment")
]
