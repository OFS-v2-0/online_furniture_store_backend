"""Файл-конфиг приложения заказы."""
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Конфиг для приложения заказы."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Заказы'
