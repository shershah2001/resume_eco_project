from django.shortcuts import render,get_object_or_404
from products.models import Product
from  wishlist.models import Wishlist


def home(request):
    
    product_data = Product.objects.all()
    wish_id = set()
    if request.user.is_authenticated:
        wish_id = set(
            Wishlist.objects.filter(
                user=request.user
            ).values_list("product_id", flat=True)
        )
    context={
        "product_data":product_data,
        "wish_id":wish_id,
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