"""Views для операций корзины."""
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.product.cart import CartAndFavorites
from apps.product.cart_serializers import (
    CartItemCreateDictSerializer,
    CartItemCreateSerializer,
    CartModelDictSerializer,
    CartModelSerializer,
    FavoriteCreateSerializer,
    FavoriteSerializer,
    ProductFavoriteSerializer,
)
from apps.product.models import CartItem, CartModel, Favorite, Product


@extend_schema(responses={status.HTTP_200_OK: CartModelSerializer}, methods=['GET'])
@api_view(['GET'])
def cart_items(request):
    """Возвращает данные о товарах в корзине пользователя."""
    user = request.user
    if user.is_authenticated:
        cart, _ = CartModel.objects.get_or_create(user=user)
        serializer = CartModelSerializer(instance=cart, context={'request': request})
        return Response(serializer.data)
    cart = CartAndFavorites(request=request)
    cart_items = cart.extract_items_cart()
    serializer = CartModelDictSerializer(instance=cart_items, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    request=CartItemCreateSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=CartModelSerializer, description='Успешное добавление товара в корзину'
        )
    },
    methods=['POST'],
)
@api_view(['POST'])
def add_cartitem(request):
    """Добавляет товар в корзину/обновляет его количество. Количество изменяется на приходящее количество товара."""
    user = request.user
    if not user.is_authenticated:
        cart = CartAndFavorites(request=request)
        serializer = CartItemCreateDictSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        cart.add(product_id=serializer.data.get('product'), quantity=serializer.data.get('quantity'))
        cart_items = cart.extract_items_cart()
        serializer = CartModelDictSerializer(instance=cart_items, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    serializer = CartItemCreateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    cart = get_object_or_404(CartModel, user=user)
    product = get_object_or_404(Product, pk=request.data['product'])
    quantity = request.data.get('quantity', 1)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        cart_item.quantity = int(quantity)
        cart_item.save(update_fields=('quantity',))
    serializer = CartModelSerializer(instance=cart, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    parameters=[OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description='Идентификатор продукта')],
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=CartModelSerializer, description='Успешное удаление товара из корзины'
        )
    },
    methods=['DELETE'],
)
@api_view(['DELETE'])
def delete_cartitem(request, id):
    """Удаляет товар из корзины."""
    product = get_object_or_404(Product, id=id)
    user = request.user
    if not user.is_authenticated:
        cart = CartAndFavorites(request=request)
        cart.remove(product_id=product.id)
        cart_items = cart.extract_items_cart()
        serializer = CartModelDictSerializer(instance=cart_items, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    cart = user.cartmodel
    instance = get_object_or_404(CartItem, product=product, cart=cart)
    instance.delete()
    serializer = CartModelSerializer(instance=cart, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(responses={status.HTTP_200_OK: FavoriteSerializer}, methods=['GET'])
@api_view(['GET'])
def favorite_list(request):
    """Возвращает данные о товарах в избранном пользователя."""
    user = request.user
    if user.is_authenticated:
        favorite_products = Product.objects.filter(favorites__user=user)
        serializer = ProductFavoriteSerializer(instance=favorite_products, many=True, context={'request': request})
        return Response(serializer.data)
    cart = CartAndFavorites(request=request)
    cart_items = cart.extract_items_favorites()
    serializer = FavoriteSerializer(instance=cart_items, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    request=FavoriteCreateSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=FavoriteSerializer, description='Успешное добавление товара в избранное'
        )
    },
    methods=['POST'],
)
@api_view(['POST'])
def add_favorite(request):
    """Добавляет товар в избранное."""
    user = request.user
    product = get_object_or_404(Product, pk=request.data['product'])

    if not user.is_authenticated:
        favorites = CartAndFavorites(request=request)
        serializer = FavoriteCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        favorites.add_to_favorites(product_id=serializer.data.get('product'))
        fav_items = favorites.extract_items_favorites()
        serializer = FavoriteSerializer(instance=fav_items, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    Favorite.objects.get_or_create(user=user, product=product)
    favorite_products = Product.objects.filter(favorites__user=user)
    serializer = ProductFavoriteSerializer(instance=favorite_products, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    parameters=[OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description='Идентификатор продукта')],
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=FavoriteSerializer, description='Успешное удаление товара из избранного'
        )
    },
    methods=['DELETE'],
)
@api_view(['DELETE'])
def delete_favorite(request, id):
    """Удаляет товар из избранного."""
    product = get_object_or_404(Product, id=id)
    user = request.user
    if not user.is_authenticated:
        favorites = CartAndFavorites(request=request)
        favorites.remove_from_favorites(product.id)
        fav_items = favorites.extract_items_favorites()
        serializer = FavoriteSerializer(instance=fav_items, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    favorite = Favorite.objects.filter(user=user, product=product).first()
    if favorite:
        favorite.delete()
    favorite_products = Product.objects.filter(favorites__user=user)
    serializer = ProductFavoriteSerializer(instance=favorite_products, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
