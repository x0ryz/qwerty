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

class Model(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]
        verbose_name = "Model"
        verbose_name_plural = "Models"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    model = models.ForeignKey(Model, related_name="products", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])

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

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.image.name}"