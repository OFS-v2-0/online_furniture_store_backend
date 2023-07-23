from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin

from apps.product.models import (
    CartItem,
    CartModel,
    Category,
    Collection,
    Color,
    Discount,
    Favorite,
    FurnitureDetails,
    FurniturePicture,
    Material,
    Product,
    ProductType,
)
from config.settings.base import ADMIN_EMPTY_VALUE_DISPLAY

User = get_user_model()


class CartItemInLine(admin.TabularInline):
    model = CartItem
    extra = 1


class DiscountInLine(admin.TabularInline):
    model = Discount.applied_products.through
    extra = 1
    verbose_name = 'Скидка'
    verbose_name_plural = 'Скидки'


class FavoriteInLine(admin.TabularInline):
    model = Favorite
    extra = 1
    verbose_name_plural = 'В избранном'


@admin.register(Category)
class CategoriesAdmin(ImportExportModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    ordering = ('pk',)
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY


@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    list_display = ('pk', 'name')
    search_fields = ('name',)
    ordering = ('pk',)
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY


@admin.register(FurnitureDetails)
class FurnitureDetailsAdmin(ImportExportModelAdmin):
    list_display = ('pk', 'purpose', 'furniture_type', 'construction', 'swing_mechanism', 'armrest_adjustment')
    search_fields = ('purpose', 'furniture_type', 'construction', 'swing_mechanism', 'armrest_adjustment')
    list_filter = ('purpose', 'furniture_type', 'construction', 'swing_mechanism', 'armrest_adjustment')
    ordering = ('pk',)
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = (
        'pk',
        'article',
        'name',
        'collection',
        'category',
        'brand',
        'country',
        'color',
        'material',
        'legs_material',
        'furniture_details',
        'price',
        'fast_delivery',
        'preview',
    )
    list_editable = ('price', 'fast_delivery')
    inlines = (DiscountInLine, FavoriteInLine, CartItemInLine)
    search_fields = ('article', 'name', 'brand')
    list_filter = ('article', 'name', 'category')
    readonly_fields = ('preview',)
    ordering = ('pk',)
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY

    def preview(self, obj):
        images_html = ''
        if obj.images and obj.images.main_image:
            images_html = f'<img src="{obj.images.main_image.url}" style="max-height: 150px;">'
        return mark_safe(images_html)


@admin.register(CartModel)
class CartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'created_at', 'updated_at')
    inlines = (CartItemInLine,)
    search_fields = ('user', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at', 'updated_at')
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'cart', 'product', 'quantity', 'created_at', 'updated_at')
    search_fields = ('cart', 'product')
    list_filter = ('cart', 'product')
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'user')
    search_fields = ('product', 'user')
    list_filter = ('product', 'user')
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY


@admin.register(Color)
class ColorAdmin(ImportExportModelAdmin):
    list_display = ('pk', 'name')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('pk',)
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY


@admin.register(Discount)
class DiscountAdmin(ImportExportModelAdmin):
    list_display = ('pk', 'discount', 'discount_created_at', 'discount_end_at')
    exclude = ('applied_products',)
    inlines = (DiscountInLine,)
    search_fields = ('discount', 'discount_created_at', 'discount_end_at')
    list_filter = ('discount', 'discount_created_at', 'discount_end_at')
    ordering = ('pk',)
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY


@admin.register(Collection)
class CollectionAdmin(ImportExportModelAdmin):
    list_display = ('name', 'slug')
    search_fields = list_display
    list_filter = list_display
    prepopulated_fields = {'slug': ('name',)}


@admin.register(FurniturePicture)
class FurniturePictureAdmin(ImportExportModelAdmin):
    list_display = ('main_image', 'first_image', 'second_image', 'third_image')
    search_fields = list_display
    list_filter = list_display


@admin.register(ProductType)
class ProductTypeAdmin(ImportExportModelAdmin):
    list_display = ('pk', 'name')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = ADMIN_EMPTY_VALUE_DISPLAY
