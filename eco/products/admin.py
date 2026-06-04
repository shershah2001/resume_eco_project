from django.contrib import admin
from products.models import Category,Product,productImage
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


class ProductImageInline(admin.TabularInline):
    model=productImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines=[ProductImageInline]
    list_display=["name","price","stock","category"]



