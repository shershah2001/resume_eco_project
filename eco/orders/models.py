from django.db import models
from account.models import MyUser,AddressModel
from products.models import Product
from variations.models import ProductVariant
import uuid

class Order(models.Model):

    PAYMENT_METHOD = (
        ("COD", "Cash On Delivery"),
        ("RAZORPAY", "Razorpay"),
        ("STRIPE", "Stripe"),
        ("PAYPAL", "Paypal"),
    )

    PAYMENT_STATUS = (
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    )

    ORDER_STATUS = (
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Packed", "Packed"),
        ("Shipped", "Shipped"),
        ("Out For Delivery", "Out For Delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )


    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name="order"
    )

    order_id = models.CharField(
        max_length=100,
        unique=True
    )

    shipping_address = models.ForeignKey(
        AddressModel,
        on_delete=models.SET_NULL,
        null=True
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    shipping_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="Pending"
    )

    order_status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS,
        default="Pending"
    )

    ordered_at = models.DateTimeField(
        auto_now_add=True
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    razorpay_order_id = models.CharField(
    max_length=200,
    blank=True,
    null=True
)

    razorpay_payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    discount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
)
    payment_id = models.CharField(
    max_length=255,
    blank=True,
    null=True
)

    def __str__(self):
        return self.order_id
    
    # yaha chora hai maine

    def save(self,*args,**kwargs):
        if not self.order_id:
             self.order_id = f"ORD-{str(uuid.uuid4())[0:8].upper()}"
        super().save(*args,**kwargs)


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items"
    )
    
    product_name = models.CharField(
        max_length=255
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product_name} ({self.quantity})"


class invoice_model(models.Model):
    invoice_number = models.CharField(max_length=200)
    orders = models.OneToOneField(Order,on_delete=models.CASCADE,related_name="invoice")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.orders.user}"


#  refund model

class refund(models.Model):
    refund_id = models.CharField(max_length=250, unique=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_receipt = models.CharField(max_length=200)
    refund_currency = models.CharField(max_length=250)
    refund_payment_id = models.CharField(max_length=100)
    refund_created_at = models.DateTimeField()
    created_at  = models.DateTimeField(auto_now_add=True)
    refund_status = models.CharField(max_length=100)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.refund_id} {self.refund_amount} {self.refund_currency}"

class RazorpayWebhookEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)  # unique=True zaroori hai
    event_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)