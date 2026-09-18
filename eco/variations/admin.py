from django.contrib import admin
from .models import ProductVariant


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'color',
        'size',
        'sku',
        'price',
        'stock',
        'is_active',
    )

    list_filter = (
        'color',
        'size',
        'is_active',
    )

    search_fields = (
        'product__name',
        'sku',
    )