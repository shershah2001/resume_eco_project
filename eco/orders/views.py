from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from carts.models  import Cart,CartItem
from account.models import AddressModel
from django.shortcuts import redirect
from products.models import  Product
from orders.models  import Order,OrderItem
from django.contrib import messages
import uuid

@login_required
def PlaceOrder(request):
    cart_item = CartItem.objects.filter(cart__user = request.user)
    if not cart_item.exists():
        messages.error(request,"please select the items")
        return redirect("cart")
    else:
        address = AddressModel.objects.filter(user = request.user).first()
        if address is None:
            messages.error(request,"please give your address")
            return redirect('address')
        for item in cart_item:
            stock = item.product.stock
            if item.quantity > stock:
                messages.error(request,"Stock not Available")
            total_price += item.sub_total
            tax_percentage = 10
            under_distance = 500
            above_distance  = 500

            if above_distance:
                shipping_charge = 100
            elif under_distance:
                shipping_charge = 200
            else:
                shipping_charge = 0
            tax_cal = (total_price  * 10) / 100
            totalAmount = total_price + tax_cal + shipping_charge
        
        Order_create = Order.objects.create(
            user=request.user,
            shipping_address = address,
            subtotal = total_price,
            tax = tax_cal,
            total_amount = totalAmount
            payment_method = request.POST.get("payment_method")
            order_id = 
        )