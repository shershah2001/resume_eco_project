from django.db import models
from account.models import MyUser
from products.models import Product, Category
from orders.models import Order
# Create your models here.


class coupons(models.Model):

    DISCOUNT_TYPES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    active = models.BooleanField(default=True)

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    used_count = models.PositiveIntegerField(
        default=0
    )

    per_user_limit = models.PositiveIntegerField(
        default=1
    )

    products = models.ManyToManyField(
        Product,
        blank=True
    )

    categories = models.ManyToManyField(
        Category,
        blank=True
    )

    first_order_only = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.code

class CouponUsage(models.Model):

    coupon = models.ForeignKey(
        coupons,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    used_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("coupon", "user", "order")