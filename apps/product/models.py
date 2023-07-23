from decimal import Decimal

from django.core.validators import MaxValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from apps.users.models import User


class Category(models.Model):
    """Модель категорий товаров в магазине."""

    name = models.CharField(verbose_name='Название категории', max_length=20, unique=True)
    slug = models.SlugField(verbose_name='Ссылка на категорию', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Material(models.Model):
    """Модель материалов товаров в магазине."""

    name = models.CharField(verbose_name='Название материала', max_length=20, unique=True)

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ('name',)

    def __str__(self):
        return self.name


class FurniturePicture(models.Model):
    main_image = models.ImageField(verbose_name='Фотография продукта', default='products/noimage_detail.png')
    first_image = models.ImageField(
        verbose_name='Фотография продукта', default='products/noimage_detail.png', blank=True
    )
    second_image = models.ImageField(
        verbose_name='Фотография продукта', default='products/noimage_detail.png', blank=True
    )
    third_image = models.ImageField(
        verbose_name='Фотография продукта', default='products/noimage_detail.png', blank=True
    )

    class Meta:
        verbose_name = 'Изображение мебели'
        verbose_name_plural = 'Изображения мебели'
        ordering = ('pk',)

    def __str__(self):
        return self.main_image.name


class Color(models.Model):
    """Модель цветов товаров в магазине."""

    name = models.CharField(verbose_name='Название цвета', max_length=20, unique=True)

    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Collection(models.Model):
    """Модель коллекции мебели."""

    name = models.CharField(verbose_name='Коллекция', max_length=100, unique=True)
    slug = models.SlugField(verbose_name='Идентификатор URL на коллекцию', max_length=100, unique=True)
    image = models.ImageField(verbose_name='Изображение коллекции', default='products/noimage_detail.png')

    class Meta:
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'
        ordering = ('id',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class FurnitureDetails(models.Model):
    """Особенности конструкции"""

    purpose = models.CharField(verbose_name='Назначение', max_length=50, blank=True, null=True)
    furniture_type = models.CharField(verbose_name='Тип', max_length=50, blank=True, null=True)
    construction = models.CharField(verbose_name='Конструкция', max_length=50, blank=True, null=True)
    swing_mechanism = models.CharField(verbose_name='Механизм качания', max_length=50, blank=True, null=True)
    armrest_adjustment = models.CharField(
        verbose_name='Регулирование подлокотников', max_length=50, blank=True, null=True
    )

    class Meta:
        verbose_name = 'Особенности конструкции'
        verbose_name_plural = 'Особенности конструкций'
        constraints = (
            models.UniqueConstraint(
                fields=('purpose', 'furniture_type', 'construction', 'swing_mechanism', 'armrest_adjustment'),
                name='unique_details',
            ),
        )
        ordering = ('purpose',)

    def __str__(self):
        fields = [
            str(field)
            for field in [
                self.pk,
                self.purpose,
                self.furniture_type,
                self.construction,
                self.swing_mechanism,
                self.armrest_adjustment,
            ]
            if field
        ]
        return ', '.join(fields) if fields else 'FurnitureDetails object'


class ProductType(models.Model):
    """Тип мебели."""

    name = models.CharField(verbose_name='Название типа мебели', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Тип мебели'
        verbose_name_plural = 'Типы мебели'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель Продуктов(Товаров) магазина"""

    article = models.PositiveIntegerField(verbose_name='Артикул', unique=True)
    name = models.CharField(verbose_name='Название', max_length=20)
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        verbose_name='Тип мебели',
        related_name='products',
        blank=True,
        null=True,
    )
    width = models.PositiveSmallIntegerField(verbose_name='Ширина, см', validators=[MaxValueValidator(15000)])
    height = models.PositiveSmallIntegerField(verbose_name='Высота, см', validators=[MaxValueValidator(15000)])
    length = models.PositiveSmallIntegerField(verbose_name='Длина, см', validators=[MaxValueValidator(15000)])
    weight = models.DecimalField(
        verbose_name='Вес, кг', validators=[MaxValueValidator(500)], decimal_places=2, max_digits=5
    )
    color = models.ForeignKey(Color, verbose_name='Цвет', on_delete=models.CASCADE, related_name='products')
    images = models.ForeignKey(
        FurniturePicture,
        verbose_name='Изображения товара',
        on_delete=models.SET_NULL,
        related_name='products',
        blank=True,
        null=True,
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        verbose_name='Материал основания',
        related_name='products',
        blank=True,
        null=True,
    )
    legs_material = models.ForeignKey(
        Material,
        verbose_name='Материал опор',
        on_delete=models.SET_NULL,
        related_name='products_legs',
        blank=True,
        null=True,
    )
    furniture_details = models.ForeignKey(
        FurnitureDetails,
        verbose_name='Особенности конструкции',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
    )
    fast_delivery = models.BooleanField(verbose_name='Быстрая доставка', default=False)
    country = models.CharField(verbose_name='Страна-производитель', max_length=40)
    brand = models.CharField(verbose_name='Бренд', null=True, max_length=100)
    warranty = models.PositiveSmallIntegerField(
        verbose_name='Гарантия , лет', null=True, validators=[MaxValueValidator(100)]
    )
    price = models.DecimalField(verbose_name='Цена', null=False, max_digits=10, decimal_places=2)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE, related_name='products')
    collection = models.ForeignKey(
        Collection, verbose_name='Коллекция', on_delete=models.SET_NULL, related_name='products', blank=True, null=True
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name',)

    def __str__(self):
        return f'{self.article} - {self.name}'

    def extract_discount(self):
        """Возвращает скидку на продукт."""
        now = timezone.now()
        return (
            self.discounts.filter(
                models.Q(discount_created_at=now, discount_end_at__gte=now)
                | models.Q(discount_created_at__lte=now, discount_end_at__gte=now)
            ).aggregate(max_discount=models.Max('discount'))['max_discount']
            or 0
        )

    def calculate_total_price(self):
        """Возвращает рассчитанную итоговую цену товара с учётом скидки."""
        discount = self.extract_discount()
        return self.price * Decimal(1 - discount / 100)


class Discount(models.Model):
    """Модель скидок для товаров в магазине."""

    applied_products = models.ManyToManyField(Product, verbose_name='Применяемые товары', related_name='discounts')
    discount = models.SmallIntegerField(verbose_name='Размер скидки, %', validators=[MaxValueValidator(99)], default=0)
    discount_created_at = models.DateField(verbose_name='Начало скидки', default=timezone.now)
    discount_end_at = models.DateField(verbose_name='Окончание скидки')

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
        ordering = ('discount_created_at',)

    def __str__(self):
        return f'{self.discount}% от {self.discount_created_at} до {self.discount_end_at}'


class Favorite(models.Model):
    """Модель для добавления товаров в избранное."""

    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='favorites', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранные товары'
        constraints = (models.UniqueConstraint(fields=('product', 'user'), name='product_user_unique'),)

    def __str__(self):
        return f'{self.user} -> {self.product}'


class CartModel(models.Model):
    """Модель корзины пользователя."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cartmodels')
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Корзина пользователя'
        verbose_name_plural = 'Корзины пользователей'

    def __str__(self):
        return f'Cart of {self.user.email}'


class CartItem(models.Model):
    """Модель содержимого корзины пользователя"""

    cart = models.ForeignKey(CartModel, verbose_name='Корзина', on_delete=models.CASCADE, related_name='cartitems')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE, related_name='cartitems')
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=0)
    created_at = models.DateTimeField(verbose_name='Дата добавления в корзину', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата обновления в корзине', auto_now=True)

    class Meta:
        verbose_name = 'Корзина с товарами'
        verbose_name_plural = 'Корзины с товарами'

    def __str__(self):
        return f'{self.product.name} {self.quantity}'
