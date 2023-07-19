from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.product.filters import ProductsFilter
from apps.product.models import Category, Collection, Color, Discount, Favorite, FurnitureDetails, Material, Product
from apps.product.serializers import (
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

    queryset = Discount.objects.all()
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

    queryset = Product.objects.all()
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
            }
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if request.method == 'POST':
            serializer = ShortProductSerializer(product, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Favorite.objects.get_or_create(user=request.user, product=product)
            return Response(serializer.data, status=HTTP_201_CREATED)
        get_object_or_404(Favorite, user=request.user, product=product).delete()
        return Response(status=HTTP_204_NO_CONTENT)

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
