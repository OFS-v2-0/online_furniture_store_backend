"""Классы представлений для пользователей."""
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.orders.models import Order
from apps.orders.serializers import OrderReadSerializer
from apps.users.serializers import UserSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для пользователя магазина."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False)
    def my_orders(self, request):
        """Заказы пользователя."""
        queryset = Order.objects.filter(user=request.user)
        serializer = OrderReadSerializer(queryset, many=True)
        return Response(serializer.data)
