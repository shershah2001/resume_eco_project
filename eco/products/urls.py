from django.urls import path
from products import views


urlpatterns = [
    path('product-detail/<slug:slug>/',views.single_product,name="product-detail")   
]
