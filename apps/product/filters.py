"""Модуль с фильтрами. """
from django.db.models import F, Q
from django_filters import rest_framework as filters

from apps.product.models import Category, Collection, Color, Material, Product


class ProductsFilter(filters.FilterSet):
    """Фильтр для приложения продукты."""

    category = filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(), field_name='category__slug', to_field_name='slug'
    )
    collection = filters.ModelMultipleChoiceFilter(
        queryset=Collection.objects.all(), field_name='collection__slug', to_field_name='slug'
    )
    color = filters.ModelMultipleChoiceFilter(
        queryset=Color.objects.all(), field_name='color__name', to_field_name='name'
    )
    brand = filters.CharFilter(lookup_expr='exact')
    fast_delivery = filters.BooleanFilter()
    min_total_price = filters.NumberFilter(method='filter_total_price', lookup_expr='gte')
    max_total_price = filters.NumberFilter(method='filter_total_price', lookup_expr='lte')
    weight = filters.RangeFilter()
    warranty = filters.RangeFilter()
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    in_stock = filters.BooleanFilter(method='filter_in_stock')
    min_rating = filters.NumberFilter(field_name='ratings__average_rating', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='ratings__average_rating', lookup_expr='lte')
    name = filters.CharFilter(method='filter_name')
    material = filters.ModelMultipleChoiceFilter(
        queryset=Material.objects.all(), field_name='material__name', to_field_name='name'
    )
    purpose = filters.CharFilter(field_name='furniture_details__purpose', lookup_expr='exact')
    furniture_type = filters.CharFilter(field_name='furniture_details__furniture_type', lookup_expr='exact')
    construction = filters.CharFilter(field_name='furniture_details__construction', lookup_expr='exact')
    swing_mechanism = filters.CharFilter(field_name='furniture_details__swing_mechanism', lookup_expr='exact')
    armrest_adjustment = filters.CharFilter(field_name='furniture_details__armrest_adjustment', lookup_expr='exact')

    class Meta:
        model = Product
        fields = (
            'category',
            'collection',
            'brand',
            'color',
            'fast_delivery',
            'min_total_price',
            'max_total_price',
            'weight',
            'warranty',
            'is_favorited',
            'in_stock',
            'min_rating',
            'max_rating',
            'material',
            'purpose',
            'furniture_type',
            'construction',
            'swing_mechanism',
            'armrest_adjustment',
        )

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация товаров по тем, что добавлены в избранное."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_in_stock(self, queryset, name, value):
        """Фильтрация товаров по тем, что есть на складе."""
        if value:
            return queryset.filter(storehouse__quantity__gt=0)
        return queryset

    def filter_total_price(self, queryset, name, value):
        """Фильтрация товаров по цене."""
        if value is not None:
            queryset = queryset.annotate(total_price=F('price') * (1 - F('discounts') / 100))
            min_total_price = self.data.get('min_total_price')
            max_total_price = self.data.get('max_total_price')
            if min_total_price and max_total_price:
                return queryset.filter(
                    Q(Q(discounts__discount__isnull=True) and Q(price__range=(min_total_price, max_total_price)))
                    | Q(total_price__range=(min_total_price, max_total_price))
                )
            elif min_total_price:
                return queryset.filter(
                    Q(Q(discounts__discount__isnull=True) and Q(price__gte=min_total_price))
                    | Q(total_price__gte=min_total_price)
                )
            elif max_total_price:
                return queryset.filter(
                    Q(Q(discounts__discount__isnull=True) and Q(price__lte=max_total_price))
                    | Q(total_price__lte=max_total_price)
                )
        return queryset

    def filter_name(self, queryset, name, value):
        """Фильтрация товаров по названию."""
        return queryset.filter(name__icontains=value)
