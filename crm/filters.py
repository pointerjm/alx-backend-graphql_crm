import django_filters
from .models import Customer, Product, Order
from django.db.models import Q

class CustomerFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(lookup_expr='icontains')
    email_icontains = django_filters.CharFilter(lookup_expr='icontains')
    created_at__gte = django_filters.DateTimeFromToRangeFilter()
    created_at__lte = django_filters.DateTimeFromToRangeFilter()
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern')
    
    class Meta:
        model = Customer
        fields = {
            'name': ['icontains'],
            'email': ['icontains'],
            'created_at': ['gte', 'lte'],
        }
    
    def filter_phone_pattern(self, queryset, name, value):
        return queryset.filter(phone__startswith=value)

class ProductFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(lookup_expr='icontains')
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock__lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['gte', 'lte'],
            'stock': ['gte', 'lte'],
        }
    
    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

class OrderFilter(django_filters.FilterSet):
    total_amount__gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount__lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date__gte = django_filters.DateTimeFromToRangeFilter()
    order_date__lte = django_filters.DateTimeFromToRangeFilter()
    customer_name = django_filters.CharFilter(method='filter_customer_name')
    product_name = django_filters.CharFilter(method='filter_product_name')
    product_id = django_filters.UUIDFilter(method='filter_product_id')
    
    class Meta:
        model = Order
        fields = {
            'total_amount': ['gte', 'lte'],
            'order_date': ['gte', 'lte'],
        }
    
    def filter_customer_name(self, queryset, name, value):
        return queryset.filter(customer__name__icontains=value)
    
    def filter_product_name(self, queryset, name, value):
        return queryset.filter(products__name__icontains=value).distinct()
    
    def filter_product_id(self, queryset, name, value):
        return queryset.filter(products__id=value).distinct()