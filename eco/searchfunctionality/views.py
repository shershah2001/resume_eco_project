from django.shortcuts import render
from products.models import Product
from searchfunctionality.search import searchfun
from django.core.paginator import Paginator

# Create your views here.

def searchview(request):

    qs = Product.objects.all().order_by('-id')

    product_filter = searchfun(
        request.GET,
        queryset=qs
    )

    paginator = Paginator(product_filter.qs, 3)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    print("Search Query:", request.GET.get("search"))
    print("Total Results:", product_filter.qs.count())

    for item in page_obj:
        print("Product:", item.name)

    context = {
        "product": page_obj,
        "search_filter": product_filter,
    }

    return render(
        request,
        'search/searchpage.html',
        context
    )