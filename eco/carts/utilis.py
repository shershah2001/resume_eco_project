
def _cart_id_(request):
    cart_id  = request.session.session_key
    if  not  cart_id:
        request.session.create()
        cart_id  = request.session.session_key
    return cart_id 