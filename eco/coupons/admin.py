from django.contrib import admin
from .models import coupons, CouponUsage


@admin.register(coupons)
class CouponsAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "min_amount",
        "valid_from",
        "valid_to",
        "active",
        "used_count",
    )

    search_fields = ("code",)

    list_filter = (
        "active",
        "discount_type",
        "first_order_only",
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):

    list_display = (
        "coupon",
        "user",
        "order",
        "discount_amount",
        "used_at",
    )