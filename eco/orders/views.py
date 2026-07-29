from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from carts.models  import Cart,CartItem
from account.models import AddressModel
from django.shortcuts import redirect
from products.models import  Product
from orders.models  import Order,OrderItem
from django.contrib import messages
import uuid
import json
import razorpay
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from orders.models import orders
@login_required
def PlaceOrder(request):
    
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request method"
        }, status=405)
    data = json.loads(request.body)
    payment_method = data.get("paymentMethod")
    address_id = data.get('addressId')
    razorpayPaymentId=data.get("razorpay_payment_id")
    razorpayOrderId = data.get("razorpay_order_id")
    razorpaySignature = data.get("razorpay_signature")

    cart_item = CartItem.objects.filter(cart__user=request.user)

   
    if not cart_item.exists():
        print("Cart is Empty")
        return JsonResponse({
        "status": "error",
        "message": "Cart is empty."
    }, status=400)
    try:
        address = AddressModel.objects.get(
            id=address_id,
            user=request.user
        )
    except AddressModel.DoesNotExist:
        print("Address Not Found")
        return JsonResponse({
        "status": "error",
        "message": "Please select a valid address."
    }, status=400)

    total_price = 0
    tax_percentage = 10
  
    # Calculate subtotal and check stock
    for item in cart_item:
        if item.quantity > item.product.stock:
            print("Out of Stock:", item.product.name)
            return JsonResponse({
            "status": "error",
            "message": f"{item.product.name} is out of stock."
        }, status=400)
        

        total_price += item.sub_total
        

    # Shipping Charge
    shipping_charge = 100

    # Tax Calculation
    tax_cal = (total_price * tax_percentage) / 100

    # Grand Total
    totalAmount = total_price + tax_cal + shipping_charge

    
    if payment_method == "RAZORPAY":
        payment_status = "Paid"
    else:
        payment_status = "Pending"
    # Create Order
    print("Before Order Create")
    order = Order.objects.create(
    user=request.user,
    shipping_address=address,
    subtotal=total_price,
    tax=tax_cal,
    shipping_charge=shipping_charge,
    total_amount=totalAmount,

    payment_method=payment_method,
    payment_status=payment_status,
    razorpay_order_id=razorpayOrderId,
    razorpay_payment_id=razorpayPaymentId,
    razorpay_signature=razorpaySignature

)
    print("After Order Create")
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
    
    return JsonResponse({
        "status": "success",
        "message": "Order created successfully",
        "order_id": order.order_id,
        "payment_method": order.payment_method,
})

def verify_payment(request):
    if request.method == "POST":
        data  = json.loads(request.body)

        # prepare parameter dictionary 
        params_dict={
            "razorpay_payment_id" :data["razorpay_payment_id"],
            "razorpay_order_id" : data["razorpay_order_id"],
            "razorpay_signature" : data["razorpay_signature"]
        }
        # initialize the offical client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(params_dict)
            return JsonResponse({"status":"success","message":"Payment verified successfully!"},status=200)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"error":"Invalid payment signature."},status=400)
    return JsonResponse({"error":"invalid request method"},status=405)

@login_required
def cancelorder(request):
    order_data = json.load(request.body)
    id  = order_data.id 
    order = get_object_or_404(orders,id=id,user=request.user)
    product_data = get_object_or_404(Product,user=request.user)
    if order.status in ["Pending","Confirmed"]:
        order.delete()
        for item in product_data.all():
            item.stock += 
    



        
