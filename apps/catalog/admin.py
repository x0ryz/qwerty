from django.contrib import admin
from .models import (
    Category,
    Brand,
    Color,
    Switch,
    Product,
    ProductVariant,
    ProductImage
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex']
    search_fields = ['name']


@admin.register(Switch)
class SwitchAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'created', 'updated']
    list_filter = ['brand', 'category', 'created']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline]
    list_per_page = 20


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['sku', 'product', 'color', 'switch', 'price', 'available']
    list_editable = ['price', 'available']
    list_filter = ['available', 'color', 'switch', 'product__brand']
    search_fields = ['sku', 'product__name']

    list_select_related = ('product', 'color', 'switch')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'is_main']
    list_filter = ['is_main']
