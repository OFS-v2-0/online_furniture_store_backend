from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.orders.models import Delivery, DeliveryType, Order
from apps.orders.serializers import (
    DeliverySerializer,
    DeliveryTypeSerializer,
    OrderReadSerializer,
    OrderWriteSerializer,
)


class DeliveryTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для способов доставки."""

    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer


class DeliveryViewSet(viewsets.ModelViewSet):
    """Вьюсет для доставок."""

    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer


class OrderViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """Вьюсет для заказов. Создание заказа либо получение заказов."""

    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return OrderReadSerializer
        return OrderWriteSerializer

    @action(detail=True, methods=['post'])
    def payment_confirmation(self, request, pk):
        """Оплата заказа."""

        order = self.get_object()
        order.paid = True
        order.save(update_fields=['paid'])
        return Response({'detail': 'Заказ успешно оплачен.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def save_total_cost(self, request, pk):
        """Сохранение общей стоимости заказа."""

        order = self.get_object()
        order.total_cost = order.order_products.aggregate(Sum('cost'))['cost__sum']
        order.save(update_fields=['total_cost'])
        return Response({'detail': 'Заказ обновлен.'}, status=status.HTTP_201_CREATED)
