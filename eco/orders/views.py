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
from razorpay.errors import BadRequestError, ServerError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from orders.models import invoice_model,refund

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.utils import timezone
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .models import Order, RazorpayWebhookEvent

import logging
logger = logging.getLogger(__name__)
from django.db import transaction, IntegrityError
from coupons.models import coupons,CouponUsage

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
    razorpayPaymentId = data.get("razorpay_payment_id")
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

    total_price = request.session.get('checkout_subtotal')
    tax_cal = request.session.get('checkout_tax')
    shipping_charge = request.session.get('checkout_shipping')
    totalAmount = request.session.get('checkout_total')
    discount_amount = request.session.get(
        'checkout_discount',
        0
    )
    if totalAmount is None:
        return JsonResponse({
            "status": "error",
            "message": "Checkout session expired. Please try again."
        }, status=400)

    if payment_method == "RAZORPAY" and razorpayOrderId:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        rzp_order = client.order.fetch(razorpayOrderId)
        razorpay_order_amount = rzp_order['amount'] / 100  # paise → rupees
        totalAmount = razorpay_order_amount  # sabse authoritative source

    if payment_method == "RAZORPAY":
        if not razorpayOrderId:
            return JsonResponse({
                "status": "error",
                "message": "Razorpay order ID is missing."
            }, status=400)

        if not razorpayPaymentId:   
            return JsonResponse({
                "status": "error",
                "message": "Razorpay payment ID is missing."
            }, status=400)
        client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

        # Razorpay Order fetch
        rzp_order = client.order.fetch(razorpayOrderId)
        # Razorpay Payment fetch
        rzp_payment = client.payment.fetch(razorpayPaymentId)
        # Payment kis order ka hai?
        if rzp_payment["order_id"] != razorpayOrderId:
            return JsonResponse({
                "status": "error",
                "message": "Payment does not belong to this order."
            }, status=400)
        # Payment captured hai ya nahi?
        if rzp_payment["status"] != "captured":
            return JsonResponse({
                "status": "error",
                "message": "Payment has not been captured."
            }, status=400)
        # Razorpay order amount
        razorpay_order_amount = rzp_order["amount"] / 100
        # Razorpay payment amount
        razorpay_payment_amount = rzp_payment["amount"] / 100
        # Amount match
        if razorpay_payment_amount != razorpay_order_amount:
            return JsonResponse({
                "status": "error",
                "message": "Payment amount does not match the order amount."
            }, status=400)
        totalAmount = razorpay_order_amount
        payment_status = "Paid"
    else:
        payment_status = "Pending"
    # Create Order
    print("Before Order Create")

    coupon_code = request.session.get("coupon_code")

    if coupon_code:
        coupon_obj = coupons.objects.filter(
            code=coupon_code,
            active=True
        ).first()

        if not coupon_obj:
            return JsonResponse({
                "status": "error",
                "message": "Coupon is no longer valid."
            }, status=400)
        now = timezone.now()
        
        if now < coupon_obj.valid_from or now > coupon_obj.valid_to:
            return JsonResponse({
                "status": "error",
                "message": "Coupon has expired or is not active yet."
            }, status=400)
        if (coupon_obj.usage_limit is not None
        and coupon_obj.used_count >= coupon_obj.usage_limit):
            return JsonResponse({
                "status": "error",
                "message": "Coupon usage limit has been reached."
            }, status=400)

        user_usage_count = CouponUsage.objects.filter(
            coupon=coupon_obj,
            user=request.user
        ).count()

        if user_usage_count >= coupon_obj.per_user_limit:
            return JsonResponse({
                "status": "error",
                "message": "You have already used this coupon."
            }, status=400)
        
    order = Order.objects.create(
            user=request.user,
            shipping_address=address,
            subtotal=total_price,
            tax=tax_cal,
            shipping_charge=shipping_charge,
            total_amount=totalAmount,
            discount=discount_amount,
            payment_method=payment_method,
            payment_status=payment_status,
            razorpay_order_id=razorpayOrderId,
            razorpay_payment_id=razorpayPaymentId,
            razorpay_signature=razorpaySignature
        )
    
    if coupon_code:
        CouponUsage.objects.create(
        coupon=coupon_obj,
        user=request.user,
        order=order,
        discount_amount=discount_amount
    )

        coupon_obj.used_count += 1
        coupon_obj.save(update_fields=['used_count'])

    for key in [
        'checkout_subtotal',
        'checkout_tax',
        'checkout_shipping',
        'checkout_total',
        'checkout_discount',
        'coupon_code'
    ]:
         request.session.pop(key, None)

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
    createInvoice(order)
    return JsonResponse({
        "status": "success",
        "message": "Order created successfully",
        "order_id": order.order_id,
        "payment_method": order.payment_method,
})


@login_required
def verify_payment(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request method"
        }, status=405)

    data = json.loads(request.body)

    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_signature = data.get("razorpay_signature")

    if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
        return JsonResponse({
            "status": "error",
            "message": "Payment details are missing."
        }, status=400)

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    params_dict = {
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_order_id": razorpay_order_id,
        "razorpay_signature": razorpay_signature
    }

    try:

        # 1. Verify Razorpay signature
        client.utility.verify_payment_signature(params_dict)

        # 2. Fetch payment from Razorpay
        payment = client.payment.fetch(razorpay_payment_id)

        # 3. Check payment belongs to the same Razorpay order
        if payment["order_id"] != razorpay_order_id:
            return JsonResponse({
                "status": "error",
                "message": "Payment does not belong to this order."
            }, status=400)

        # 4. Check payment status
        if payment["status"] != "captured":
            return JsonResponse({
                "status": "error",
                "message": f"Payment is not captured. Current status: {payment['status']}"
            }, status=400)

        return JsonResponse({
            "status": "success",
            "message": "Payment verified successfully.",
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_order_id": razorpay_order_id
        })

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid payment signature."
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)

def createInvoice(order):

    invoice_number = f"INV-{order.order_id}"

    invoice = invoice_model.objects.create(
        invoice_number=invoice_number,
        orders=order
    )

    subject = f"Your Invoice - {invoice_number}"

    from_email = "shershahcode@gmail.com"

    to_email = order.user.email

    print("================================")
    print("USER:", order.user)
    print("USER EMAIL:", repr(to_email))
    print("FROM EMAIL:", from_email)
    print("================================")

    # Check user email
    if not to_email:
        print("ERROR: User email is empty.")
        return invoice

    html_content = render_to_string(
        "orders/invoice.html",
        {
            "user_name": order.user.first_name,
            "order": order,
            "invoice": invoice,
        }
    )

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email],
    )

    msg.attach_alternative(
        html_content,
        "text/html"
    )

    # Actually send email
    result = msg.send(fail_silently=False)

    print("EMAIL SEND RESULT:", result)

    return invoice

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
        order_id=orderId,
        user=request.user
    )

    if order.order_status not in ["Pending", "Confirmed"]:
        return JsonResponse({
            "status": "error",
            "message": "This order cannot be cancelled."
        }, status=400)

    order_items = OrderItem.objects.filter(order=order)

    try:

        # ==========================
        # RAZORPAY REFUND
        # ==========================

        if (
            order.payment_status == "Paid"
            and order.payment_method == "RAZORPAY"
        ):

            # Check whether refund already exists
            existing_refund = refund.objects.filter(
                order=order

            ).first()

            if existing_refund:

                return JsonResponse({
                    "status": "error",
                    "message": "Refund has already been initiated for this order."
                }, status=400)

            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                )
            )

            refund_receipt = (
                f"REFUND-{order.order_id}-{uuid.uuid4().hex[:8]}"
            )

            refund_response = client.payment.refund(
                order.razorpay_payment_id,
                {
                    "amount": int(order.total_amount * 100),
                    "speed": "normal",
                    "notes": {
                        "order_id": order.order_id
                    },
                    "receipt": refund_receipt
                }
            )

            # ==========================
            # SAVE REFUND IN DATABASE
            # ==========================

            refund.objects.create(
                refund_id=refund_response["id"],
                refund_amount=order.total_amount,
                refund_receipt=refund_receipt,
                refund_currency=refund_response["currency"],
                refund_payment_id=refund_response["payment_id"],
                refund_created_at=timezone.now(),
                refund_status=refund_response["status"],
                order=order
            )

            order.payment_status = "Refunded"

        # ==========================
        # RESTORE STOCK
        # ==========================

        for item in order_items:

            if item.product:
                item.product.stock += item.quantity
                item.product.save()

        # ==========================
        # CANCEL ORDER
        # ==========================

        order.order_status = "Cancelled"
        order.save()

        return JsonResponse({
            "status": "success",
            "message": "Your order has been cancelled successfully.",
            "order_id": order.order_id
        })

    except BadRequestError as e:

        return JsonResponse({
            "status": "Failed",
            "message": e.args[0]
        }, status=400)

    except ServerError as e:

        return JsonResponse({
            "status": "Failed",
            "message": e.args[0]
        }, status=500)

    except Exception as e:

        return JsonResponse({
            "status": "Failed",
            "message": str(e)
        }, status=500)


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
    
@csrf_exempt
def razorpay_webhook(request):

    # 1. Sirf POST request allow karo
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=405)

    # 2. Raw payload lo
    payload = request.body.decode('utf-8')

    # 3. Razorpay signature lo
    sig_header = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')

    if not sig_header:
        return JsonResponse({
            'status': 'error',
            'message': 'Signature missing'
        }, status=400)

    # 4. Razorpay Event ID lo
    event_id = request.META.get('HTTP_X_RAZORPAY_EVENT_ID')

    if not event_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Event ID missing'
        }, status=400)

    try:

        # 5. Signature verify karo
        verify_signature(payload, sig_header)

        # 6. JSON payload ko Python dictionary mein convert karo
        try:
            event = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.exception("Invalid JSON payload received")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid payload'
            }, status=400)

        event_type = event.get('event')

        logger.info("Webhook event received: %s (event_id=%s)", event_type, event_id)

        # 7. Poora processing ek transaction ke andar karo,
        # taaki duplicate-check + order-update + event-save
        # sab ek saath atomic ho (race condition se bachne ke liye)
        with transaction.atomic():

            # 6a. Duplicate webhook check + reserve karo (atomic dedup)
            # get_or_create ke saath unique constraint hone se
            # do parallel requests ek hi event ko dobara process
            # nahi kar payenge
            try:
                event_obj, created = RazorpayWebhookEvent.objects.select_for_update().get_or_create(
                    event_id=event_id,
                    defaults={'event_type': event_type}
                )
            except IntegrityError:
                # Agar race condition mein dusra request pehle hi
                # insert kar chuka hai
                created = False

            if not created:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Event already processed'
                })

            # ==========================================
            # PAYMENT CAPTURED
            # ==========================================

            if event_type == 'payment.captured':

                payment = event.get('payload', {}).get('payment', {}).get('entity')

                if not payment:
                    logger.error("payment.captured event missing payment entity: %s", event)
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Malformed payment payload'
                    }, status=400)

                payment_id = payment.get('id')
                order_id = payment.get('order_id')

                try:
                    order = Order.objects.select_for_update().get(
                        razorpay_order_id=order_id
                    )

                    order.razorpay_payment_id = payment_id
                    order.payment_verified = True
                    order.payment_status = 'Paid'

                    order.save()

                except Order.DoesNotExist:
                    logger.error("Order not found for order_id=%s (payment_id=%s)", order_id, payment_id)
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Order not found'
                    }, status=404)

            # ==========================================
            # REFUND PROCESSED
            # ==========================================

            elif event_type == 'refund.processed':

                refund = event.get('payload', {}).get('refund', {}).get('entity')

                if not refund:
                    logger.error("refund.processed event missing refund entity: %s", event)
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Malformed refund payload'
                    }, status=400)

                refund_id = refund.get('id')
                payment_id = refund.get('payment_id')

                logger.info("Refund processed: refund_id=%s payment_id=%s", refund_id, payment_id)

                try:
                    order = Order.objects.select_for_update().get(
                        razorpay_payment_id=payment_id
                    )

                    order.payment_status = 'Refunded'

                    # Agar refund_id field banaya hai:
                    # order.razorpay_refund_id = refund_id

                    order.save()

                except Order.DoesNotExist:
                    logger.error("Order not found for refund: payment_id=%s", payment_id)
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Order not found for refund'
                    }, status=404)

            # ==========================================
            # REFUND FAILED
            # ==========================================

            elif event_type == 'refund.failed':

                refund = event.get('payload', {}).get('refund', {}).get('entity')

                if not refund:
                    logger.error("refund.failed event missing refund entity: %s", event)
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Malformed refund payload'
                    }, status=400)

                refund_id = refund.get('id')
                payment_id = refund.get('payment_id')

                logger.info("Refund failed: refund_id=%s payment_id=%s", refund_id, payment_id)

                try:
                    order = Order.objects.select_for_update().get(
                        razorpay_payment_id=payment_id
                    )

                    order.payment_status = 'Refund Failed'
                    order.save()

                except Order.DoesNotExist:
                    logger.error("Order not found for failed refund: payment_id=%s", payment_id)
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Order not found for refund'
                    }, status=404)

            # 8. Yahan tak pahunche matlab processing successful raha,
            # event_obj already create ho chuka hai upar (get_or_create mein)

        # 9. Razorpay ko 200 response
        return JsonResponse({
            'status': 'success',
            'message': 'Webhook processed successfully'
        })

    except razorpay.errors.SignatureVerificationError:
        logger.warning("Invalid webhook signature received")
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid signature'
        }, status=400)

    except Exception:
        # Production mein actual error log karo,
        # user ko internal details mat bhejo
        logger.exception("Webhook processing failed")
        return JsonResponse({
            'status': 'error',
            'message': 'Webhook processing failed'
        }, status=500)

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)
def verify_signature(payload, sig_header):
    return client.utility.verify_webhook_signature(
        payload,
        sig_header,
        settings.RAZORPAY_WEBHOOK_SECRET
    )