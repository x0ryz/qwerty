from django.contrib import admin
from .models import (
    Category, Brand, Product, ProductVariant, ProductImage,
    Attribute, AttributeValue,
    KeyboardSpecification, KeycapSpecification, SwitchSpecification
)


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AttributeValueInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['available_attributes']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    show_change_link = True


class KeyboardSpecInline(admin.StackedInline):
    model = KeyboardSpecification
    extra = 0
    verbose_name = "Характеристики клавіатури"

class KeycapSpecInline(admin.StackedInline):
    model = KeycapSpecification
    extra = 0
    verbose_name = "Характеристики кейкапів"

class SwitchSpecInline(admin.StackedInline):
    model = SwitchSpecification
    extra = 0
    verbose_name = "Характеристики свічів"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'created']
    list_filter = ['category', 'brand', 'created']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    inlines = [
        ProductImageInline,
        ProductVariantInline,
        KeyboardSpecInline,
        KeycapSpecInline,
        SwitchSpecInline
    ]

    fieldsets = (
        ('Основне', {
            'fields': ('category', 'brand', 'name', 'slug', 'description')
        }),
    )