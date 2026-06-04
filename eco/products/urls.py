from django.urls import path
from products import views


urlpatterns = [
    path('product-detail/<slug:product_slug>/',views.single_product,name="product_detail")   
]
