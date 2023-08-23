"""Модуль представления для приложения отзывов."""
from rest_framework.viewsets import ModelViewSet

from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer
from common.permisions import IsOwner


class ReviewViewSet(ModelViewSet):
    """Представление для отзывов."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsOwner,)
