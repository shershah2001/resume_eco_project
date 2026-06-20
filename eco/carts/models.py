from django.db import models
from products.models import Product
from account.models import MyUser
# Create your models here.


class Cart(models.Model):
    user=models.ForeignKey(MyUser,null=True,blank=True, on_delete=models.CASCADE)
    guest_user = models.CharField(max_length=250,blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"{self.user.username}"
        return f"{self.guest_user}"
    
    

class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} {self.cart}"
    
    @property
    def sub_total(self):
        return self.product.price * self.quantity

