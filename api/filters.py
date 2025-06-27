import django_filters
from core.models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(field_name="category__name", lookup_expr="iexact")
    color = django_filters.CharFilter(field_name="color__name", lookup_expr="icontains")
    size = django_filters.CharFilter(field_name="size__name", lookup_expr="icontains")
    is_featured = django_filters.BooleanFilter(field_name="is_featured")
    
    class Meta:
        model = Product
        fields = ["category", "color", "size", "min_price", "max_price", "is_featured"]
