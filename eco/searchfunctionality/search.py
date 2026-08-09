import django_filters
from django.db.models import Q
from products.models import Product

class searchfun(django_filters.FilterSet):
    
    search = django_filters.CharFilter(method='filter_by_all')

    class Meta:
        model = Product
        fields = ['search']

    def filter_by_all(self,queryset,name,value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(category__category_name__icontains=value)
        )