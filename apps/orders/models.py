from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum, UniqueConstraint

from apps.product.models import Product

User = get_user_model()


class DeliveryType(models.Model):
    """Модель способов доставки"""

    name = models.CharField(verbose_name='Способ доставки', max_length=20, unique=True)

    class Meta:
        verbose_name = 'Способ доставки'
        verbose_name_plural = 'Способы доставки'

    def __str__(self):
        return self.name


class Delivery(models.Model):
    """Модель доставки"""

    address = models.CharField(verbose_name='Адрес', max_length=200)
    type_delivery = models.ForeignKey(
        DeliveryType,
        verbose_name='Способ доставки',
        on_delete=models.SET_NULL,
        related_name='delivery',
        null=True,
        blank=True,
    )
    comment = models.CharField(verbose_name='Комментарий к доставек', blank=True)
    datetime_from = models.DateTimeField(verbose_name='Дата/время доставки от')
    datetime_to = models.DateTimeField(verbose_name='Дата/время доставки до')
    elevator = models.BooleanField(verbose_name='Наличие лифта', default=False)

    class Meta:
        verbose_name = 'Доставка'
        verbose_name_plural = 'Доставка'

    def __str__(self):
        return self.address


class Order(models.Model):
    """Модель заказов"""

    user = models.ForeignKey(
        User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='orders', null=True
    )
    products = models.ManyToManyField(Product, through='OrderProduct', verbose_name='Товар')
    created = models.DateTimeField(verbose_name='Дата заказа', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Дата обновления заказа', auto_now=True)
    delivery = models.ForeignKey(
        Delivery, verbose_name='Доставка', on_delete=models.SET_NULL, related_name='orders', null=True, blank=True
    )
    total_cost = models.DecimalField(
        verbose_name='Общая стоимость', default=0.00, max_digits=40, decimal_places=2, null=True, blank=True
    )
    paid = models.BooleanField(verbose_name='Оплачено', default=False)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ: {self.id} - {self.user.email}'


class OrderProduct(models.Model):
    """Модель товаров в заказе"""

    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE, related_name='order_products')
    price = models.DecimalField(verbose_name='Цена', max_digits=20, decimal_places=2)
    quantity = models.PositiveIntegerField(
        verbose_name='Колличество',
        validators=[MinValueValidator(1, message='Минимальное количество: 1 шт.')],
        default=1,
    )
    cost = models.DecimalField(verbose_name='Стоимость', max_digits=40, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Товары в заказе'
        verbose_name_plural = 'Товары в заказах'
        constraints = [UniqueConstraint(fields=['order', 'product'], name='unique_product_order')]

    def __str__(self):
        return f'{self.order}, товар: {self.product}'

    def save(self, *args, **kwargs):
        self.price = self.product.price
        self.cost = self.price * self.quantity
        super().save(*args, **kwargs)

        self.order.total_cost = self.order.order_products.aggregate(Sum('cost'))['cost__sum']
        self.order.save(update_fields=['total_cost'])


class Storehouse(models.Model):
    """Модель товаров на складе"""

    product = models.OneToOneField(Product, verbose_name='Товар', on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(verbose_name='Количество товара', default=0)

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склад'

    def __str__(self):
        return f'{self.product}, количество: {self.quantity}'
