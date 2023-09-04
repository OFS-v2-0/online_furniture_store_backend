"""Views для операций корзины."""
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.product.cart import Cart
from apps.product.cart_serializers import (
    CartItemCreateDictSerializer,
    CartItemCreateSerializer,
    CartModelDictSerializer,
    CartModelSerializer,
)
from apps.product.models import CartItem, CartModel, Product


@extend_schema(responses={status.HTTP_200_OK: CartModelSerializer}, methods=['GET'])
@api_view(['GET'])
def cart_items(request, pk=None):
    """Возвращает данные о товарах в корзине пользователя."""
    user = request.user
    if user.is_authenticated:
        cart, _ = CartModel.objects.get_or_create(user=user)
        serializer = CartModelSerializer(instance=cart, context={'request': request})
        return Response(serializer.data)
    cart = Cart(request=request)
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
def add_item(request):
    """Добавляет товар в корзину/обновляет его количество. Количество изменяется на приходящее количество товара."""
    user = request.user
    if not user.is_authenticated:
        cart = Cart(request=request)
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
def del_item(request, id):
    """Удаляет товар из корзины."""
    product = get_object_or_404(Product, id=id)
    user = request.user
    if not user.is_authenticated:
        cart = Cart(request=request)
        cart.remove(product_id=product.id)
        cart_items = cart.extract_items_cart()
        serializer = CartModelDictSerializer(instance=cart_items, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    cart = user.cartmodel
    instance = get_object_or_404(CartItem, product=product, cart=cart)
    instance.delete()
    serializer = CartModelSerializer(instance=cart, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
