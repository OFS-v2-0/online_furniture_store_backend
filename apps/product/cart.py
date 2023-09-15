from django.conf import settings

from apps.product.models import Product


class CartAndFavorites:
    """Корзина товаров не авторизованного пользователя."""

    def __init__(self, request, user=None):
        """Инициализация корзины."""
        self.session = request.session
        self.user = user
        self.cart = self.session.get(settings.CART_SESSION_ID) or {}
        self.favorites = self.session.get(settings.FAV_SESSION_ID) or {}

    def __len__(self):
        """Количество всех товаров в корзине."""
        return sum(item.get('quantity') for item in self.cart.values())

    def extract_items_cart(self):
        """Возвращает содержимое корзины."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products = [
            {'product': product, 'quantity': self.cart[str(product.id)].get('quantity')} for product in products
        ]
        return {'products': products}

    def add(self, product_id, quantity=1):
        """Добавить продукт в корзину или обновить его количество."""
        self.cart[str(product_id)] = {'quantity': quantity}
        self.save()

    def save(self):
        """Сохраняет данные в сессии."""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session[settings.FAV_SESSION_ID] = self.favorites
        self.session.modified = True

    def remove(self, product_id):
        """Удаление товара из корзины."""
        if str(product_id) in self.cart:
            del self.cart[str(product_id)]
            self.save()

    def clear(self):
        """Удаляет корзину из сессии."""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def add_to_favorites(self, product_id):
        """Добавить товар в избранное."""
        self.favorites[str(product_id)] = True
        self.save()

    def remove_from_favorites(self, product_id):
        """Удалить товар из избранного."""
        if str(product_id) in self.favorites:
            del self.favorites[str(product_id)]
            self.save()

    def clear_favorites(self):
        """Удаляет корзину из сессии."""
        del self.session[settings.FAV_SESSION_ID]
        self.session.modified = True

    def extract_items_favorites(self):
        """Возвращает содержимое избранного."""
        product_ids = self.favorites.keys()
        products = Product.objects.filter(id__in=product_ids)
        return {'products': products}
