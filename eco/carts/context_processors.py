from .models import Cart,CartItem
from django.shortcuts  import get_object_or_404
from .utilis import _cart_id_


def cart_value(request):
    count_quantity=0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            cart_id = _cart_id_(request)
            cart = Cart.objects.get(guest_user=cart_id)
        cartItem=CartItem.objects.filter(cart=cart)
        for item in cartItem:
            count_quantity += item.quantity 
    except Cart.DoesNotExist:
        pass
    return {
        'count_quantity':count_quantity
    }
    
