from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def get_absolute_url(self):
        return reverse("catalog:product_list_by_category", args=[self.slug])

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=255)
    hex = models.CharField(max_length=6)

    def __str__(self):
        return self.name

class Switch(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    brand = models.ForeignKey(Brand, related_name="products", on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])

    def get_main_image_url(self):
        if hasattr(self, 'main_img_list') and self.main_img_list:
            return self.main_img_list[0].image.url
        img = self.images.filter(is_main=True).first()
        if img:
            return img.image.url
        return '/static/img/no-image.png'

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["created"]),
        ]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name="variants", on_delete=models.PROTECT)
    switch = models.ForeignKey(Switch, related_name="variants", on_delete=models.PROTECT, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    sku = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.product.name} - {self.color.name} ({self.switch.name})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name="images", on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - {self.color.name if self.color else 'General'} - {self.image.name}"