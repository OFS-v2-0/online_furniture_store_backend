"""Админка для приложения отзывов."""
from django.contrib import admin

from apps.reviews.models import Rating, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'product', 'rating')
    search_fields = ('product', 'user')
    list_filter = ('product', 'user')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'average_rating')
    search_fields = ('product',)
    list_filter = ('product',)
