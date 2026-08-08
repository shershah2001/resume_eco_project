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
from  django.templatetags.static import static
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

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request method"
        }, status=405)

    data = json.loads(request.body)

    orderId = data.get("order_id")

    order = get_object_or_404(
        Order,
        id=orderId,
        user=request.user
    )

    if order.order_status not in ["Pending", "Confirmed"]:
        return JsonResponse({
            "status": "error",
            "message": "This order cannot be cancelled."
        }, status=400)

    order_items = OrderItem.objects.filter(order=order)

    for item in order_items:
        if item.product:
            item.product.stock += item.quantity
            item.product.save()

    order.order_status = "Cancelled"
    order.save()

    return JsonResponse({
        "status": "success",
        "message": "Your order has been cancelled successfully.",
        "order_id": order.order_id
    })


def serialize_orders(user_orders):
    data_arr = []
    
    for item in user_orders:
        data_img = item.items.first()
        if data_img and data_img.product and data_img.product.image:
            img = data_img.product.image.url
        else:
            img = static('default_product/pro_img.png')

        orderQuantity = item.items.count()
        data_arr.append({
            "orderId": item.order_id,
            "shipping_address": item.shipping_address.address,
            "subtotal": item.subtotal,
            "tax": item.tax,
            "shipping_charge": item.shipping_charge,
            "total_amount": item.total_amount,
            "payment_method": item.payment_method,
            "order_status": item.order_status,
            'image':img,
            'orderAt':item.ordered_at,
            'orderQuantity':orderQuantity,
            'deliveredAt':item.delivered_at,
            'paymentStatus':item.payment_status
        })
    return data_arr

@login_required
def all_orders(request):
    user_order = Order.objects.filter(user=request.user)
    return JsonResponse(serialize_orders(user_order),safe=False)

@login_required
def myorders(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Method Not Allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    status = data.get("order_status")

    valid_status = [
        "All Orders",
        "Pending",
        "Confirmed",
        "Delivered",
        "Cancelled",
    ]

    if status not in valid_status:
        return JsonResponse(
            {"error": "Invalid order status"},
            status=400
        )

    if status == "All Orders":
        user_orders = Order.objects.filter(user=request.user)
        
    else:
        user_orders = Order.objects.filter(
            user=request.user,
            order_status=status
        )
    return JsonResponse(serialize_orders(user_orders), safe=False)

@login_required
def orderdetail(request):
    ordId = request.GET.get("ordId")
    detail_data = get_object_or_404(Order,order_id=ordId,user=request.user)
    items = []
    for item in detail_data.items.all():
        items.append({
        "product_name": item.product.name,
        "image": item.product.image.url,
        "price": item.price,
        "quantity": item.quantity,
    })
    return JsonResponse({
    "orderId": detail_data.order_id,
    "shipping_address": detail_data.shipping_address.address,
    "subtotal": detail_data.subtotal,
    "tax": detail_data.tax,
    "shipping_charge": detail_data.shipping_charge,
    "total_amount": detail_data.total_amount,
    "payment_method": detail_data.payment_method,
    "payment_status": detail_data.payment_status,
    "order_status": detail_data.order_status,
    "ordered_at": detail_data.ordered_at.isoformat() if detail_data.ordered_at else None,
    "delivered_at": detail_data.delivered_at.isoformat() if detail_data.delivered_at else None,
    "razorpayOrderId": detail_data.razorpay_order_id,
    "razorpayPaymentId": detail_data.razorpay_payment_id,
    "razorpaySignature": detail_data.razorpay_signature,
    "discount": detail_data.discount,
    "paymentId": detail_data.payment_id,
    "items":items
})
    



