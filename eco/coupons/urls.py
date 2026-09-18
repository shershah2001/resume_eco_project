from django.urls import path
from coupons import views

urlpatterns = [
   path('apply-coupon/',views.coupon_views,name="apply_coupon")
]
