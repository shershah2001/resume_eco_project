from django.shortcuts import render
from products.models import Product
from searchfunctionality.search import searchfun
from django.core.paginator import Paginator

# Create your views here.

def searchview(request):
    qs = Product.objects.all()
    pro_filter = searchfun(request.GET,queryset=qs)
    paginator = Paginator(pro_filter.qs,3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context={
        "product":page_obj
    }
    return render(request,'search/searchpage.html',context)