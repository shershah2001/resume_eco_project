from django.shortcuts import render,redirect
from carts.models import CartItem,Cart
from products.models import Product
from django.shortcuts import get_object_or_404
# Create your views here.



def cartView(request):
    cart_item =CartItem.objects.filter(cart__user=request.user)
    total_price =0
    quantity=0
    tax_percentage  = 10
    grand_total=0
    for item in cart_item:
        total_price  += item.price 
        quantity += item.quantity
    grand_total = total_price  + (total_price * tax_percentage)/100
    context={
        "cart_item":cart_item,
        "total_price":total_price,
        "quantity":quantity,
        "grand_total":grand_total
    }
    return render(request,'cart.html',context)

def add_to_cart(request,product_slug):
    product=get_object_or_404(Product,slug=product_slug)
    cart,created=Cart.objects.get_or_create(user=request.user)
    cartItem,cartItem_created = CartItem.objects.get_or_create(cart=cart,product=product)

    if not cartItem_created:
        cartItem.quantity  +=1
    else:
        cartItem.quantity=1
    cartItem.price = product.price * cartItem.quantity
    cartItem.save()

    return redirect('cart')


def remove_to_cart(request,product_slug):
    product = get_object_or_404(Product,slug=product_slug)
    cart = get_object_or_404(Cart,user = request.user)
    if cart:
        cart_item=CartItem.objects.filter(cart=cart,product=product)
        for item in cart_item:
            if item.quantity > 1:
                item.quantity -=1
                item.price = product.price * item.quantity
                item.save()
            else:
                item.delete()
            
    return redirect('cart')


def increaseView(request,product_slug):
    if request.method == "POST":
        product = get_object_or_404(Product,slug=product_slug)
        cart = get_object_or_404(Cart,user=request.user)
        cart_item=get_object_or_404(CartItem,cart=cart,product=product)

        cart_item.quantity += 1
        cart_item.price = product.price * cart_item.quantity
        cart_item.save()
    return redirect('cart')
    

def decreaseView(request,product_slug):
    if request.method=="POST":
        product=get_object_or_404(Product,slug=product_slug)
        cart=get_object_or_404(Cart,user=request.user)
        cart_item=get_object_or_404(CartItem,cart=cart,product=product)

        if cart_item.quantity > 1:
            cart_item.quantity-=1
            cart_item.price = product.price * cart_item.quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')

