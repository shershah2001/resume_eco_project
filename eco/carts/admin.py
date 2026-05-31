from django.contrib import admin
from carts.models import Cart
from carts.models import CartItem
# Register your models here.


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display=['user','created_at','updated_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display=["product","cart","quantity","created_at","updated_at","is_active"]

