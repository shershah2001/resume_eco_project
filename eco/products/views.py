from django.shortcuts import render,get_object_or_404
from products.models import Product

# Create your views here.



def home(request):
    data = Product.objects.all()
    # print("==>",data)
    context={
        "data":data
    }
    return render(request,"home.html",context)

def single_product(request,product_slug):
    single_product = get_object_or_404(Product,slug=product_slug)
    images = single_product.sub_productImages.all()

    context={
        'single_product':single_product,
        'images':images
    }

    return render(request,"product/single_product.html",context)