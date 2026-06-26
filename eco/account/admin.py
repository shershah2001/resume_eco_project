from django.contrib import admin
from .models import MyUser,AddressModel,UserProfileModel
# Register your models here.


@admin.register(MyUser)
class MyUserAdminModel(admin.ModelAdmin):
    list_display=['username','first_name','last_name','profile_image','email']


@admin.register(AddressModel)
class AddressModelAdmin(admin.ModelAdmin):
    list_display=["name","mobile","pincode","locality","address","city","state","landmark","alternate_mobile","address_type",'email']


@admin.register(UserProfileModel)
class UserProfileModelAdmin(admin.ModelAdmin):
    list_display=["user","first_name","last_name","gender","email","mobile"]