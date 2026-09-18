from decimal import Decimal

from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

from .models import coupons, CouponUsage
from carts.models import Cart, CartItem
from orders.models import Order
from django.db import models

def coupon_views(request):

    if request.method != "POST":
        return redirect("checkout")

    code = request.POST.get(
        "coupon_code",
        ""
    ).strip()

    if not code:
        messages.error(
            request,
            "Please enter coupon code"
        )
        return redirect("checkout")


    coupon_obj = coupons.objects.filter(
        code=code
    ).first()

    if coupon_obj is None:
        messages.error(
            request,
            "Invalid coupon code"
        )
        return redirect("checkout")


    if not coupon_obj.active:
        messages.error(
            request,
            "This coupon is inactive"
        )
        return redirect("checkout")


    now = timezone.now()

    if now < coupon_obj.valid_from:
        messages.error(
            request,
            "This coupon is not active yet"
        )
        return redirect("checkout")

    if now > coupon_obj.valid_to:
        messages.error(
            request,
            "This coupon has expired"
        )
        return redirect("checkout")


    if (
        coupon_obj.usage_limit is not None
        and coupon_obj.used_count >= coupon_obj.usage_limit
    ):
        messages.error(
            request,
            "This coupon usage limit has been reached"
        )
        return redirect("checkout")

    cart = Cart.objects.filter(
        user=request.user
    ).first()

    if cart is None:
        messages.error(
            request,
            "Cart not found"
        )
        return redirect("checkout")

    cart_items = CartItem.objects.filter(
        cart=cart,
        is_active=True
    ).select_related("product")

    if not cart_items.exists():
        messages.error(
            request,
            "Your cart is empty"
        )
        return redirect("checkout")


    subtotal = sum(
        (
            item.sub_total
            for item in cart_items
        ),
        Decimal("0")
    )

    if subtotal < coupon_obj.min_amount:
        messages.error(
            request,
            f"Minimum order amount is ₹{coupon_obj.min_amount}"
        )
        return redirect("checkout")

    user_usage_count = CouponUsage.objects.filter(
        coupon=coupon_obj,
        user=request.user
    ).count()

    if user_usage_count >= coupon_obj.per_user_limit:
        messages.error(
            request,
            "You have already used this coupon"
        )
        return redirect("checkout")

    if coupon_obj.first_order_only:

        previous_order = Order.objects.filter(
            user=request.user
        ).exists()

        if previous_order:
            messages.error(
                request,
                "This coupon is only for first order"
            )
            return redirect("checkout")

    allowed_products = coupon_obj.products.all()
    allowed_categories = coupon_obj.categories.all()

    if allowed_products.exists() or allowed_categories.exists():

        eligible_items = cart_items.filter(
            models.Q(product__in=allowed_products)
            | models.Q(product__category__in=allowed_categories)
        )

        if not eligible_items.exists():
            messages.error(
                request,
                "This coupon is not applicable to your products"
            )
            return redirect("checkout")

        eligible_subtotal = sum(
            (
                item.sub_total
                for item in eligible_items
            ),
            Decimal("0")
        )

    else:
        eligible_subtotal = subtotal

    if coupon_obj.discount_type == "percentage":
        discount = (
            eligible_subtotal *
            coupon_obj.discount_value
        ) / Decimal("100")

        # Maximum discount
        if coupon_obj.max_discount is not None:

            discount = min(
                discount,
                coupon_obj.max_discount
            )

    elif coupon_obj.discount_type == "fixed":

        discount = coupon_obj.discount_value

    else:

        messages.error(
            request,
            "Invalid discount type"
        )
        return redirect("checkout")

    discount = min(
        discount,
        eligible_subtotal
    )


    request.session["coupon_code"] = coupon_obj.code
    request.session["checkout_discount"] = str(discount)

    messages.success(
        request,
        f"{coupon_obj.code} applied!"
        f"You saved ₹{discount}"
    )

    return redirect("checkout")