"""Конфигурация приложения product."""
from django.apps import AppConfig


class ProductConfig(AppConfig):
    """Класс конфигурации приложения product."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.product'
    verbose_name = 'товары'
