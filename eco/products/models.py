from django.db import models
from django.utils.text import slugify
# Create your models here.

class Category(models.Model):
    category_name=models.CharField(max_length=100,unique=True)
    slug = models.SlugField(unique=True,blank=True)

    class Meta:
        verbose_name="Category"
        verbose_name_plural ="Categories"
    def __str__(self):
        return self.category_name
    
    def save(self,*args,**kwargs):
        if  not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args,**kwargs)

class Product(models.Model):
    name=models.CharField(max_length=100)
    slug=models.SlugField(unique=True,blank=True)
    description=models.TextField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    stock=models.IntegerField()
    image=models.ImageField(upload_to='product_image/',default="assets/static/image/default.png")
    category= models.ForeignKey(Category,on_delete=models.CASCADE)

    def save(self,*args,**kwargs):
        if not  self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)
        