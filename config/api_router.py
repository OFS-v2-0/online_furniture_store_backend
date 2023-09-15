"""Модуль подключения роутеров приложения."""
from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.orders.views import DeliveryTypeViewSet, DeliveryViewSet, OrderViewSet
from apps.product.cart_views import (
    add_cartitem,
    add_favorite,
    cart_items,
    delete_cartitem,
    delete_favorite,
    favorite_list,
)
from apps.product.views import (
    CategoryViewSet,
    CollectionViewSet,
    ColorViewSet,
    DiscountViewSet,
    MaterialViewSet,
    ProductViewSet,
    download_last_file,
)
from apps.reviews.views import ReviewViewSet
from apps.users.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('colors', ColorViewSet, basename='colors')
router.register('categories', CategoryViewSet, basename='categories')
router.register('materials', MaterialViewSet, basename='materials')
router.register('products', ProductViewSet, basename='products')
router.register('collections', CollectionViewSet, basename='collections')
router.register('reviews', ReviewViewSet, basename='reviews')
router.register('discounts', DiscountViewSet, basename='discounts')
router.register('delivery_types', DeliveryTypeViewSet, basename='delivery_types')
router.register('delivery', DeliveryViewSet, basename='delivery')
router.register('orders', OrderViewSet, basename='orders')

app_name = 'api'
urlpatterns = [
    path('carts/items/', cart_items, name='items'),
    path('carts/add_item/', add_cartitem, name='add_item'),
    path('carts/delete_item/<int:id>/', delete_cartitem, name='delete_item'),
    path('favorites/list/', favorite_list, name='fav_list'),
    path('favorites/add_favorite/', add_favorite, name='add_favorite'),
    path('favorites/delete_favorite/<int:id>/', delete_favorite, name='delete_favorite'),
    path('users/me/', UserViewSet.as_view({'get': 'me', 'post': 'create', 'patch': 'me'})),
    path('users/change_password/', UserViewSet.as_view({'post': 'set_password'}), name='user-change-password'),
    path('users/reset_password/', UserViewSet.as_view({'post': 'reset_password'}), name='user-reset-password'),
    path(
        'users/reset_password_confirm/',
        UserViewSet.as_view({'post': 'reset_password_confirm'}),
        name='user-reset-password-confirm',
    ),
    path('users/my_orders/', UserViewSet.as_view({'get': 'my_orders'}), name='user-my-orders'),
    path('download/', download_last_file, name='download_file'),
    path('', include(router.urls)),
]
