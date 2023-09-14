"""Сериализаторы для методов функционала корзины."""
from django.db.models import Sum
from rest_framework import serializers

from apps.product.models import CartItem, CartModel, Favorite, Product
from apps.product.serializers import ShortProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Сериализатор данных о товаре в корзине."""

    product = ShortProductSerializer()

    class Meta:
        model = CartItem
        fields = ('product', 'quantity')


class CartItemCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания записи содержимого корзины."""

    class Meta:
        model = CartItem
        fields = ('product', 'quantity')


class CartModelSerializer(serializers.ModelSerializer):
    """Сериализатор корзины пользователя."""

    total_quantity = serializers.SerializerMethodField(method_name='calculate_total_quantity')
    total_price = serializers.SerializerMethodField(method_name='calculate_total_price')
    total_discount_price = serializers.SerializerMethodField(method_name='calculate_total_discount_price')
    total_weight = serializers.SerializerMethodField(method_name='calculate_total_weight')

    products = CartItemSerializer(source='cartitems', many=True)

    class Meta:
        model = CartModel
        fields = ('total_quantity', 'total_price', 'total_discount_price', 'total_weight', 'products')

    def calculate_total_quantity(self, obj):
        """Возвращает общее количество товара в корзине."""
        return obj.cartitems.all().aggregate(Sum('quantity'))['quantity__sum'] or 0

    def calculate_total_price(self, obj):
        """Возвращает общую стоимость товара в корзине."""
        return sum(item.product.price * item.quantity for item in obj.cartitems.all())

    def calculate_total_discount_price(self, obj):
        """Возвращает общую сумму товара в корзине с учётом скидки."""
        return sum(item.product.calculate_total_price() * item.quantity for item in obj.cartitems.all())

    def calculate_total_weight(self, obj):
        """Возвращает общий вес товара в корзине."""
        return sum(item.product.weight * item.quantity for item in obj.cartitems.all())


class CartItemDictSerializer(serializers.Serializer):
    """Сериализатор данных о товаре в корзине."""

    product = ShortProductSerializer()
    quantity = serializers.IntegerField()


class CartModelDictSerializer(serializers.Serializer):
    """Сериализатор корзины пользователя."""

    total_quantity = serializers.SerializerMethodField(method_name='calculate_total_quantity')
    total_price = serializers.SerializerMethodField(method_name='calculate_total_price')
    total_discount_price = serializers.SerializerMethodField(method_name='calculate_total_discount_price')
    total_weight = serializers.SerializerMethodField(method_name='calculate_total_weight')
    products = CartItemDictSerializer(many=True, read_only=True)

    def calculate_total_quantity(self, obj):
        """Возвращает общее количество товара в корзине."""
        return sum(item.get('quantity') for item in obj.get('products'))

    def calculate_total_price(self, obj):
        """Возвращает общую стоимость товара в корзине."""
        return sum(item.get('product').price * item.get('quantity') for item in obj.get('products'))

    def calculate_total_discount_price(self, obj):
        """Возвращает общую сумму товара в корзине с учётом скидки."""
        return sum(item.get('product').calculate_total_price() * item.get('quantity') for item in obj.get('products'))

    def calculate_total_weight(self, obj):
        """Возвращает общий вес товара в корзине."""
        return sum(item.get('product').weight * item.get('quantity') for item in obj.get('products'))


class CartItemCreateDictSerializer(serializers.Serializer):
    """Сериализатор для создания записи содержимого корзины."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects, source='product_id')
    quantity = serializers.IntegerField(required=True, min_value=1)


# Fav
class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных товаров."""

    product = ShortProductSerializer()

    class Meta:
        model = Favorite
        fields = ('product',)


class FavoriteCreateSerializer(serializers.Serializer):
    """Сериализатор для запроса добавления товара в избранное."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product_id')

    class Meta:
        model = Favorite
        fields = ('product',)


class FavModelDictSerializer(serializers.Serializer):
    """Сериализатор корзины пользователя."""

    products = ShortProductSerializer(many=True, read_only=True)


class FavoriteListSerializer(serializers.Serializer):
    """Сериализатор для списка избранных товаров пользователя."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    products = FavoriteSerializer(many=True, read_only=True, source='favorites')

    class Meta:
        model = Favorite
        fields = ('user', 'products')
