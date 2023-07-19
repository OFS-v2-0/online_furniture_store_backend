from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from apps.product.models import (
    Category,
    Collection,
    Color,
    Discount,
    FurnitureDetails,
    FurniturePicture,
    Material,
    Product,
)


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Categories."""

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class MaterialSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Material."""

    class Meta:
        model = Material
        fields = ('id', 'name')


class ColorSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Color."""

    class Meta:
        model = Color
        fields = ('id', 'name')


class FurnitureDetailsSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели FurnitureDetails."""

    class Meta:
        model = FurnitureDetails
        fields = ('purpose', 'furniture_type', 'construction', 'swing_mechanism', 'armrest_adjustment')


class DiscountSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Discount."""

    class Meta:
        model = Discount
        fields = ('discount',)


class CollectionSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Collection."""

    image = Base64ImageField()

    class Meta:
        model = Collection
        fields = ('id', 'name', 'slug', 'image')
        read_only_fields = fields


class FurniturePictureSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения изображений товара."""

    class Meta:
        model = FurniturePicture
        fields = ('main_image', 'first_image', 'second_image', 'third_image')


class ShortProductSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения товаров."""

    is_favorited = serializers.SerializerMethodField(method_name='analyze_is_favorited')
    discount = serializers.SerializerMethodField(method_name='extract_discount')
    total_price = serializers.SerializerMethodField(method_name='calculate_total_price')
    images = Base64ImageField(required=True)
    available_quantity = serializers.SerializerMethodField(method_name='fetch_available_quantity')
    product_type = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'article',
            'product_type',
            'name',
            'is_favorited',
            'price',
            'discount',
            'total_price',
            'available_quantity',
            'images',
        )

    def analyze_is_favorited(self, obj):
        """
        Возвращает True, если товар добавлен в избранное для ползователя.
        Возвращает False, если пользователь не авторизован или товар не в избранном у пользователя.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def extract_discount(self, obj):
        """Возвращает скидку на продукт."""
        return obj.extract_discount()

    def calculate_total_price(self, obj):
        """Возвращает рассчитанную итоговую цену товара с учётом скидки."""
        return obj.calculate_total_price()

    def fetch_available_quantity(self, obj):
        """Возвращает доступное для заказ количество товара на складе."""
        return 5


class ProductSerializer(ShortProductSerializer):
    """Сериалайзер для модели Product."""

    category = CategorySerializer()
    color = ColorSerializer()
    collection = CollectionSerializer()
    images = FurniturePictureSerializer()
    material = MaterialSerializer()
    legs_material = MaterialSerializer()

    class Meta(ShortProductSerializer.Meta):
        fields = ShortProductSerializer.Meta.fields + (
            'category',
            'material',
            'legs_material',
            'collection',
            'images',
            'width',
            'height',
            'length',
            'weight',
            'fast_delivery',
            'country',
            'brand',
            'warranty',
            'description',
            'color',
        )
        read_only_fields = ('category', 'material', 'purpose', 'is_favorited')


class ProductAllColors(serializers.Serializer):
    """Сериализатор товара и таких же товаров в другом цвете."""

    product = ProductSerializer()
    other_color_same_products = ProductSerializer(many=True)
    similar_products = ProductSerializer(many=True)
