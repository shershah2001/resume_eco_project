from django.shortcuts import render,redirect
from carts.models import CartItem,Cart
from products.models import Product
from django.shortcuts import get_object_or_404
# Create your views here.
from .utilis import _cart_id_
from django.contrib.auth.decorators import login_required
from account.models import AddressModel

def cartView(request):
    if request.user.is_authenticated:
        cart_item =CartItem.objects.filter(cart__user=request.user)
    else:
        cart_id = _cart_id_(request)
        cart_item = CartItem.objects.filter(cart__guest_user = cart_id)
    total_price = 0
    quantity= 0
    tax_percentage  = 10
    grand_total= 0
    for item in cart_item:
        total_price  += item.product.price * item.quantity
        quantity += item.quantity
    grand_total = total_price  + (total_price * tax_percentage)/100
    # for item in cart_item:
    #     print("cart_item==>",item.product.image.url)
    context={
        "cart_item":cart_item,
        "sub_total":total_price,
        "quantity":quantity,
        "grand_total":grand_total,
        "tax_percentage":tax_percentage
    }
    return render(request,'cart.html',context)

def add_to_cart(request,product_slug):
    product=get_object_or_404(Product,slug=product_slug)
    if request.user.is_authenticated:
        cart,created=Cart.objects.get_or_create(user=request.user)
    else:
        cart_id  = _cart_id_(request)
        cart,created = Cart.objects.get_or_create(guest_user = cart_id)
    cartItem,cartItem_created = CartItem.objects.get_or_create(cart=cart,product=product)

    if not cartItem_created:
        cartItem.quantity  +=1
    else:
        cartItem.quantity=1
    # cartItem.price = product.price * cartItem.quantity
    cartItem.save()

    return redirect('cart')


def remove_to_cart(request,product_slug):
    product = get_object_or_404(Product,slug=product_slug)
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart,user = request.user)
    else:
        cart=get_object_or_404(Cart, guest_user = _cart_id_(request))
    if cart:
        cart_item=CartItem.objects.filter(cart=cart,product=product)
        for item in cart_item:
            if item.quantity > 1:
                item.quantity -=1
                # item.price = product.price * item.quantity
                item.save()
            else:
                item.delete()
            
    return redirect('cart')


def increaseView(request,product_slug):
    if request.method == "POST":
        product = get_object_or_404(Product,slug=product_slug)
        if  request.user.is_authenticated:
            cart = get_object_or_404(Cart,user=request.user)
        else:
            cart_id =_cart_id_(request)
            cart=get_object_or_404(Cart,guest_user = cart_id)
        cart_item=get_object_or_404(CartItem,cart=cart,product=product)

        cart_item.quantity += 1
        # cart_item.price = product.price * cart_item.quantity
        cart_item.save()
    return redirect('cart')
    

def decreaseView(request,product_slug):
    if request.method=="POST":
        product=get_object_or_404(Product,slug=product_slug)
        if request.user.is_authenticated:
            cart=get_object_or_404(Cart,user=request.user)
        else:
            cart_id  = _cart_id_(request)
            cart=get_object_or_404(Cart,guest_user=cart_id)
        cart_item=get_object_or_404(CartItem,cart=cart,product=product)

        if cart_item.quantity > 1:
            cart_item.quantity-=1
            # cart_item.price = product.price * cart_item.quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')


@login_required
def checkout(request):
    # user_address = get_object_or_404(AddressModel,user=request.user)
    user_address=AddressModel.objects.filter(user=request.user)
    context={
        "user_address":user_address
    }
    print("==>",user_address)
    return render(request,'checkout.html',context)