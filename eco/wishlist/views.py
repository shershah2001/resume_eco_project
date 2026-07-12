from django.shortcuts import render
from .models import Wishlist
from products.models import Product
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def wishlistView(request, id):

    if request.method != "POST":
        return JsonResponse({
            "error": "Only POST requests are allowed."
        }, status=405)

    product = get_object_or_404(Product,id=id)

    data = Wishlist.objects.filter(
        user=request.user,
        product=product
    )

    if data.exists():
        print("Deleting...")
        data.delete()

        wishlist_count = Wishlist.objects.filter(
        user=request.user
        ).count()

        return JsonResponse({
            "status": "removed",
            "wishlist_count":wishlist_count
        })
    
    # print("Creating...")

    Wishlist.objects.create(
        user=request.user,
        product=product,
    )
    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    return JsonResponse({
        "status": "added",
        "wishlist_count":wishlist_count
    })

@login_required
def wishlistProduct(request):
    wish_products = Wishlist.objects.filter(user=request.user).select_related('product')
    context={
        "wish_products":wish_products
    }
    return render(request,"wishlist.html",context)