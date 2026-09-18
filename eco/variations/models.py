from django.db import models
from products.models import Product


class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    color = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    size = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    sku = models.CharField(
        max_length=50,
        unique=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"

    





