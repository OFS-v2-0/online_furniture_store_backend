from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.product.filters import ProductsFilter
from apps.product.models import Category, Collection, Color, Discount, FurnitureDetails, Material, Product
from apps.product.serializers import (
    BrandSerializer,
    CategorySerializer,
    CollectionSerializer,
    ColorSerializer,
    DiscountSerializer,
    FurnitureDetailsSerializer,
    MaterialSerializer,
    ProductAllColors,
    ProductSerializer,
    ShortProductSerializer,
)


class CategoryViewSet(ReadOnlyModelViewSet):
    """Вьюсет для категорий товаров."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class MaterialViewSet(ReadOnlyModelViewSet):
    """Вьюсет для материалов товаров."""

    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


class DiscountViewSet(ReadOnlyModelViewSet):
    """Вьюсет для скидок товаров."""

    queryset = Discount.objects.all().prefetch_related('applied_products')
    serializer_class = DiscountSerializer


class ColorViewSet(ReadOnlyModelViewSet):
    """Вьюсет для цветов товаров."""

    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class FurnitureDetailsViewSet(ReadOnlyModelViewSet):
    """Вьюсет для отображения особенностей конструкции товаров."""

    queryset = FurnitureDetails.objects.all()
    serializer_class = FurnitureDetailsSerializer


class ProductViewSet(ReadOnlyModelViewSet):
    """Вьюсет для товаров."""

    queryset = Product.objects.all().select_related(
        'product_type', 'color', 'images', 'material', 'legs_material', 'furniture_details', 'category', 'collection'
    )
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductsFilter
    search_fields = ('name',)

    def retrieve(self, request, *args, **kwargs):
        """Выводит информацию о товаре и таких же товарах в другом цвете."""
        product = self.get_object()
        similar_products = self.get_queryset().filter(category=product.category)
        other_color_same_products = similar_products.filter(
            product_type=product.product_type, name=product.name
        ).exclude(color=product.color)
        serializer = ProductAllColors(
            instance={
                'product': product,
                'other_color_same_products': other_color_same_products,
                'similar_products': similar_products,
            },
            context={'request': request},
        )
        return Response(serializer.data)

    @action(detail=False)
    def popular(self, request, top=6):
        """Возвращает топ популярных товаров."""
        popular_products = (
            Product.objects.annotate(total_quantity=Sum('order_products__quantity'))
            .filter(total_quantity__gt=0)
            .order_by('-total_quantity')[:top]
        )
        serializer = ShortProductSerializer(popular_products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def materials_by_category(self, request):
        categories = Category.objects.all()
        materials_by_category = {}

        for category in categories:
            products = Product.objects.filter(category=category)
            materials = Material.objects.filter(products__in=products).distinct()
            serializer = MaterialSerializer(materials, many=True)
            materials_by_category[category.slug] = serializer.data

        return Response(materials_by_category)


class CollectionViewSet(ReadOnlyModelViewSet):
    """Вьюсет для коллекций. Только чтение одного или списка объектов."""

    queryset = Collection.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CollectionSerializer
        return ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        collection = self.get_object()
        serializer = self.get_serializer(collection.products, many=True)
        return Response(serializer.data)


@api_view(('GET',))
def brand_list(request):
    """Список брендов товаров."""
    brand_list = Product.objects.values('brand').order_by().distinct()
    serializer = BrandSerializer(brand_list, many=True)
    return Response(serializer.data)
