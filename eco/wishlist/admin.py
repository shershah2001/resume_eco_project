from django.contrib import admin
from .models import Wishlist
# Register your models here.

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user","product__name","date")
    list_filter = ("user","product__name","date")
    search_fields = ("user__username","product__name")