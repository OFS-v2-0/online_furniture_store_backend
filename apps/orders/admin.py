"""Настройка административной панели для объектов приложение orders."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from import_export.admin import ImportExportModelAdmin

from apps.orders.models import Delivery, DeliveryType, Order, OrderProduct, Storehouse

User = get_user_model()


@admin.register(DeliveryType)
class DeliveryTypeAdmin(ImportExportModelAdmin):
    """Админ модель для типа доставки."""

    list_display = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Delivery)
class DeliveryAdmin(ImportExportModelAdmin):
    """Админ модель для указания характеристик доставки."""

    list_display = ('id', 'address', 'type_delivery', 'datetime_from', 'datetime_to', 'elevator')
    search_fields = ('address',)
    list_filter = ('address', 'type_delivery')


@admin.register(OrderProduct)
class OrderProductAdmin(ImportExportModelAdmin):
    """Админ модель для модели продуктов."""

    list_display = ('id', 'order', 'product', 'quantity', 'price', 'cost')


class OrderProductInline(admin.TabularInline):
    """Инлайн модель для административной панели модели продуктов."""

    model = OrderProduct
    raw_id_fields = ('product',)
    fields = ('product', 'price', 'quantity')
    readonly_fields = ('price',)


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    """Админ модель для модели заказов."""

    list_display = ('id', 'user', 'created', 'updated', 'paid', 'delivery', 'total_cost')
    readonly_fields = ('total_cost', 'created', 'updated')
    search_fields = ('id', 'paid')
    list_filter = ('created', 'updated', 'paid', 'delivery')
    inlines = [OrderProductInline]


@admin.register(Storehouse)
class StorehouseAdmin(ImportExportModelAdmin):
    """Админ модель для модели склада."""

    list_display = ('id', 'product', 'quantity')
    search_fields = ('product',)
    list_filter = ('product',)
    ordering = ('pk',)
