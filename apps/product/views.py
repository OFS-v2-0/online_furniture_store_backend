"""Модуль представления для приложения products."""
import glob
import os

from django.conf import settings
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
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
            },
            context={'request': request},
        )
        return Response(serializer.data)

    @staticmethod
    def _fetch_favorite_products_serializer_data(request):
        """Возвращает сериализованные данные избранных товаров ползователя."""
        favorite_products = Product.objects.filter(favorites__user=request.user)
        return ShortProductSerializer(favorite_products, many=True, context={'request': request}).data

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавление товара в список избранных товаров пользователя."""
        product = get_object_or_404(Product, pk=pk)
        Favorite.objects.get_or_create(user=request.user, product=product)
        serializer_data = self._fetch_favorite_products_serializer_data(request=request)
        return Response(serializer_data, status=HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        """Удаление товара из списока избранных товаров пользователя."""
        product = get_object_or_404(Product, pk=pk)
        get_object_or_404(Favorite, user=request.user, product=product).delete()
        serializer_data = self._fetch_favorite_products_serializer_data(request=request)
        return Response(serializer_data, status=HTTP_200_OK)

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


def _get_latest_file(directory):
    """Возвращает имя полседненго изменённого файла в директории."""
    list_of_files = glob.glob(directory + '/*')
    if not list_of_files:
        raise Http404('Директория пустая или не существует')
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


@api_view(('POST',))
@permission_classes((IsAdminUser,))
def download_last_file(request):
    """Скачивает последний изменённый файл из директории EMAIL_FILE_PATH."""
    file_path = _get_latest_file(settings.EMAIL_FILE_PATH)

    if not os.path.exists(file_path):
        raise Http404('Файл не найден')

    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
        return response
