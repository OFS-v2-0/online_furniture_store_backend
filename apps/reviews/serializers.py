"""Сериализаторы приложения отзывов."""
from rest_framework import serializers

from apps.product.serializers import ShortProductSerializer
from apps.reviews.models import Review
from apps.users.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Отзывы."""

    user = UserSerializer(read_only=True)
    product = ShortProductSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('user', 'product', 'feedback', 'rating')
