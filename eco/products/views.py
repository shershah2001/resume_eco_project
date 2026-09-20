from django.shortcuts import render,get_object_or_404
from products.models import Product
from  wishlist.models import Wishlist
from django.core.paginator import Paginator
from searchfunctionality import search
from variations.models import ProductVariant
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
    variants = ProductVariant.objects.filter(
        product=single_product,
        is_active=True
    )
    unique_colors = {}

    for variant in variants:
        if variant.color:
            color_key = variant.color.lower()
            if color_key not in unique_colors:
                unique_colors[color_key] = variant

    colors = unique_colors.values()
    variant_data = []
    for variant in variants:

        variant_data.append({
            "id": variant.id,
            "color": variant.color,
            "size": variant.size,
            "price": str(variant.price),
            "stock": variant.stock,
            "image": variant.image.url if variant.image else "",
        })
    context = {
        "single_product": single_product,
        "images": images,
        "variants": variants,
        "colors": colors,
        "variant_data": variant_data,
    }
    return render(request,"product/single_product.html",context)



