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
    cart_item = CartItem.objects.filter(cart__user=request.user)

    if not cart_item.exists():
        messages.error(request, "Please select the items.")
        return redirect("cart")

    address = AddressModel.objects.filter(user=request.user).first()

    if address is None:
        messages.error(request, "Please add your address.")
        return redirect("address")

    total_price = 0
    tax_percentage = 10
  
    # Calculate subtotal and check stock
    for item in cart_item:
        if item.quantity > item.product.stock:
            messages.error(request, f"{item.product.name} is out of stock.")
            return redirect("cart")
        

        total_price += item.sub_total
        

    # Shipping Charge
    shipping_charge = 100

    # Tax Calculation
    tax_cal = (total_price * tax_percentage) / 100

    # Grand Total
    totalAmount = total_price + tax_cal + shipping_charge

    # Create Order
    order = Order.objects.create(
        user=request.user,
        shipping_address=address,
        subtotal=total_price,
        tax=tax_cal,
        shipping_charge=shipping_charge,
        total_amount=totalAmount,
        payment_method=request.POST.get("RAZORPAY"),
    )
    for item in cart_item:
        OrderItem.objects.create(
            order = order,
            product = item.product,
            product_name = item.product.name,
            quantity = item.quantity,
            price = item.product.price,
            total_price = item.sub_total
        )
        item.product.stock -= item.quantity
        item.product.save()
        item.delete()

    messages.success(request, "Order created successfully.")

    return redirect("checkout")


def verify_payment(request):
