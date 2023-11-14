"""Views для операций корзины."""
from django.shortcuts import get_object_or_404
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
from apps.product.openapi import (
    add_cartitem,
    add_favorite,
    cart_items,
    delete_cartitem,
    delete_favorite,
    favorite_list,
)


@cart_items
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


@add_cartitem
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


@delete_cartitem
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
    cart = user.cartmodels
    instance = get_object_or_404(CartItem, product=product, cart=cart)
    instance.delete()
    serializer = CartModelSerializer(instance=cart, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@favorite_list
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


@add_favorite
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


@delete_favorite
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
