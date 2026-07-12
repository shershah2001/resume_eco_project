from django.db import models
from  account.models  import MyUser
from products.models import Product
# Create your models here.


class Wishlist(models.Model):
    user  = models.ForeignKey(MyUser,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user","product")

# note ...
# unique_together se ek user ek hi product ko do baar wishlist me add nahi kar payega.
# Ye Amazon, Flipkart aur doosre ecommerce projects me bhi common pattern hai.




