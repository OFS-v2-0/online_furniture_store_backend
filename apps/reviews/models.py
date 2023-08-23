"""Модели приложения отзывов."""
from django.contrib.auth import get_user_model
from django.db import models

from apps.product.models import Product

User = get_user_model()


class Review(models.Model):
    """Модель отзывов на товары в магазине."""

    RATE_CHOICES = zip(range(1, 6), range(1, 6))
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE, related_name='reviews')
    feedback = models.TextField(verbose_name='Отзыв', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(verbose_name='Рейтинг', choices=RATE_CHOICES)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (models.UniqueConstraint(fields=('user', 'product'), name='unique_review'),)

    def __str__(self):
        return f'{self.user.email}: {self.product.name} - {self.rating}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        average_rating = self.product.reviews.aggregate(models.Avg('rating'))['rating__avg']
        rating, created = Rating.objects.get_or_create(product=self.product)
        rating.average_rating = average_rating
        rating.save()


class Rating(models.Model):
    """Модель рейтинга товара в магазине."""

    product = models.OneToOneField(Product, verbose_name='Товар', on_delete=models.CASCADE, related_name='ratings')
    average_rating = models.PositiveSmallIntegerField(verbose_name='Средний рейтинг', null=True, blank=True)

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def __str__(self):
        return self.product
