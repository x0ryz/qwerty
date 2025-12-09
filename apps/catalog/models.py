from django.db import models
from django.urls import reverse


class Attribute(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    available_attributes = models.ManyToManyField(Attribute, blank=True)

    def get_absolute_url(self):
        return reverse("catalog:product_list_by_category", args=[self.slug])

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name="products", on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])

    def get_main_image_url(self):
        img = self.images.filter(is_main=True).first()
        if not img:
            img = self.images.first()
        return img.image.url if img else '/static/img/no-image.png'

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    attributes = models.ManyToManyField(AttributeValue, related_name='variants', blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=255, unique=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} (SKU: {self.sku})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(
        AttributeValue,
        related_name="images",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Img for {self.product.name}"


class KeyboardSpecification(models.Model):
    product = models.OneToOneField(Product, related_name="keyboard_specs", on_delete=models.CASCADE)
    layout = models.CharField(max_length=50, blank=True)
    connection = models.CharField(max_length=50, blank=True)
    hot_swappable = models.BooleanField(default=False)

class KeycapSpecification(models.Model):
    product = models.OneToOneField(Product, related_name="keycap_specs", on_delete=models.CASCADE)
    material = models.CharField(max_length=50, blank=True)
    profile = models.CharField(max_length=50, blank=True)

class SwitchSpecification(models.Model):
    product = models.OneToOneField(Product, related_name="switch_specs", on_delete=models.CASCADE)
    type = models.CharField(max_length=50, blank=True)
    actuation_force = models.CharField(max_length=20, blank=True)
    pin_count = models.IntegerField(default=3)