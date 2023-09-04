"""Конфиг приложения отзывов."""
from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Конфиг приложения отзывов."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reviews'
    verbose_name = 'отзывы'
