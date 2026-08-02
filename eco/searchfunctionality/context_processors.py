from searchfunctionality.search import searchfun
from products.models import  Product
def search_context(request):
    return {
        'filter_data':searchfun(
            request.GET,
            queryset=Product.objects.none()
    )
    }