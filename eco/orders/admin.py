from django.contrib import admin

# Register your models here
from orders.models  import Order,OrderItem,invoice_model
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(invoice_model)