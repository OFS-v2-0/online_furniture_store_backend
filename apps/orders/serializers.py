from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.orders.models import Delivery, DeliveryType, Order, OrderProduct, Storehouse
from apps.users.serializers import UserSerializer

User = get_user_model()


class DeliveryTypeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели DeliveryType."""

    class Meta:
        model = DeliveryType
        fields = ('id', 'name')


class DeliverySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Delivery."""

    type_delivery = serializers.PrimaryKeyRelatedField(queryset=DeliveryType.objects.all(), allow_null=True)

    class Meta:
        model = Delivery
        fields = ('id', 'address', 'type_delivery', 'comment', 'datetime_from', 'datetime_to', 'elevator')


class OrderProductWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи товаров в заказе в модель OrderProduct."""

    class Meta:
        model = OrderProduct
        fields = ('product', 'quantity')


class OrderProductReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения товаров в заказе из модели OrderProduct."""

    id = serializers.ReadOnlyField(source='product.id')
    name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderProduct
        fields = ('id', 'name', 'quantity', 'price', 'cost')


class OrderReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения Заказов из модели Order."""

    products = OrderProductReadSerializer(many=True, source='order_products')
    delivery = DeliverySerializer()

    class Meta:
        model = Order
        fields = ('id', 'user', 'products', 'delivery', 'total_cost', 'paid')


class OrderWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи Заказов в модель Order."""

    user = UserSerializer(required=False)
    products = OrderProductWriteSerializer(many=True)
    delivery = DeliverySerializer()

    class Meta:
        model = Order
        fields = ('user', 'products', 'delivery', 'total_cost', 'paid')
        read_only_fields = ('total_cost',)

    @transaction.atomic
    def create(self, validated_data):
        """Сохраняет заказ в базе, обрновляет склад."""

        if user_data := validated_data.pop('user', {}):
            user = User.objects.create_user(**user_data)
        else:
            user = self.context['request'].user

        delivery_data = validated_data.pop('delivery')
        products = validated_data.pop('products')
        delivery = Delivery.objects.create(**delivery_data)
        order = Order.objects.create(user=user, delivery=delivery, **validated_data)
        self.update_storehouse(products)
        self.add_products(order, products)
        return order

    @staticmethod
    def update_storehouse(products):
        """Проверяет и обновляет кличество на складе после заказа."""

        storehouse = []
        for product in products:
            ordered_product = product.get('product')
            ordered_quantity = int(product.get('quantity'))
            storehouse_product = ordered_product.storehouse

            storehouse_product_quantity = storehouse_product.quantity
            if storehouse_product_quantity < ordered_quantity:
                raise ValidationError(
                    f'Для заказа товара {ordered_product} доступно {storehouse_product_quantity} шт.'
                )

            storehouse_product.quantity -= ordered_quantity
            storehouse.append(storehouse_product)

        Storehouse.objects.bulk_update(storehouse, ['quantity'])

    @staticmethod
    @transaction.atomic
    def add_products(order, products):
        """Сохраняет в базу данные заказа в OrderProduct, общую стоимость в Order."""

        OrderProduct.objects.bulk_create(
            [
                OrderProduct(
                    order=order,
                    product=product.get('product'),
                    price=product.get('product').calculate_total_price(),
                    quantity=product['quantity'],
                    cost=product.get('product').calculate_total_price() * product['quantity'],
                )
                for product in products
            ]
        )

        order.total_cost = order.order_products.aggregate(Sum('cost'))['cost__sum']
        order.save()

    def to_representation(self, instance):
        return OrderReadSerializer(instance, context={'request': self.context.get('request')}).data
