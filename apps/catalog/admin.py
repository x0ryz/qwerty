from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Attribute,
    AttributeValue,
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant,
)

# --- Inlines ---
# These allow you to edit related models on the same page as the parent.


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1  # Provides 1 empty row for new data by default


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    show_change_link = (
        True  # Allows clicking through to the full variant page if needed
    )
    # Note: Editing M2M fields (attributes) inside an inline can be clunky.
    # If you have many attributes, consider creating variants in their own dedicated view.


# --- Model Admins ---


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "id"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [
        AttributeValueInline
    ]  # Edit values like Red/Blue inside the "Color" page


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["available_attributes"]  # Better widget for ManyToMany


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "brand",
        "variant_count",
        "created",
    ]
    list_filter = ["category", "brand", "created", "updated"]
    search_fields = ["name", "slug", "brand__name"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["attributes"]
    inlines = [ProductImageInline, ProductVariantInline]

    # Custom method to show image thumbnail in the list view

    # Custom method to show how many variants exist
    def variant_count(self, obj):
        return obj.variants.count()

    variant_count.short_description = "Variants"

    # Quick check to see if it has variants and images (simulating 'published' status)
    def is_published_check(self, obj):
        return obj.variants.exists() and obj.images.exists()

    is_published_check.boolean = True
    is_published_check.short_description = "Ready?"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    # This acts as a fallback if you need to edit a variant in isolation
    list_display = ["product", "sku", "price", "available"]
    list_filter = ["available", "product__category", "product__brand"]
    search_fields = ["sku", "product__name"]
    filter_horizontal = ["attributes"]
    autocomplete_fields = ["product"]  # Useful if you have thousands of products
