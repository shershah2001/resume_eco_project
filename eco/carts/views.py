from django.shortcuts import render,redirect
from carts.models import CartItem,Cart
from products.models import Product
from django.shortcuts import get_object_or_404
# Create your views here.
from .utilis import _cart_id_
from django.contrib.auth.decorators import login_required
from account.models import AddressModel
from django.http import JsonResponse

import razorpay
from django.conf import settings

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

    user_address=AddressModel.objects.filter(user=request.user);
    selected_add = user_address.first()

    cart_items = CartItem.objects.filter(
        cart__user=request.user,
        is_active=True
    ).select_related("product")

    subtotal=0
    grand_total=0
    tax_percentage=10
    shipping=10

    for item in cart_items:
        subtotal += item.sub_total 

    tax=subtotal * tax_percentage / 100
    grand_total=subtotal+tax+shipping

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    amount = int(grand_total * 100)
    
    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })
    context={
        "user_address":user_address,
        "selected_add":selected_add,
        "cartItem":cart_items,
        "subtotal":subtotal,
        "tax":tax,
        "tax_percentage":tax_percentage,
        "shipping":shipping,
        "grand_total":grand_total,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "payment":payment,
    }

    return render(request,'checkout.html',context)

@login_required
def checkout_address(request,id):
    radio_address = get_object_or_404(AddressModel,id=id,user=request.user)
    data={
        "name":radio_address.name,
        "mobile":radio_address.mobile,
        "pincode":radio_address.pincode,
        "locality":radio_address.locality,
        "address":radio_address.address,
        "email":radio_address.email,
        "city":radio_address.city,
        "state":radio_address.state,
        "landmark":radio_address.landmark,
        "alternate_mobile":radio_address.alternate_mobile,
        "address_type":radio_address.address_type,
    }
    return JsonResponse(data);


