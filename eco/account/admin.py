from django.contrib import admin
from .models import MyUser,AddressModel,UserProfileModel
# Register your models here.

admin.site.register(MyUser)
admin.site.register(AddressModel)
admin.site.register(UserProfileModel)