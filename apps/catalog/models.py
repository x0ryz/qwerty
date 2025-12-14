from django.db import models
from django.urls import reverse


class Attribute(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(
        Attribute, related_name="values", on_delete=models.CASCADE
    )
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
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    brand = models.ForeignKey(Brand, related_name="products", on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    specs = models.JSONField(default=dict, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])

    def get_main_image_url(self):
        if hasattr(self, "main_img_list"):
            if self.main_img_list:
                return self.main_img_list[0].image.url

        else:
            img = self.images.filter(is_main=True).first()
            if not img:
                img = self.images.first()

            if img:
                return img.image.url

        return None

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, related_name="variants", on_delete=models.CASCADE
    )
    attributes = models.ManyToManyField(
        AttributeValue, related_name="variants", blank=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=255, unique=True)
    available = models.BooleanField(default=True)

    def get_image_url(self):
        attr_ids = self.attributes.values_list("id", flat=True)

        specific_image = self.product.images.filter(
            attribute_value__id__in=attr_ids
        ).first()

        if specific_image:
            return specific_image.image.url

        return self.product.get_main_image_url()

    def get_images(self):
        attr_ids = self.attributes.values_list("id", flat=True)
        images = self.product.images.filter(attribute_value__id__in=attr_ids)

        if images.exists():
            return images

        return self.product.images.all()

    def __str__(self):
        return f"{self.product.name} (SKU: {self.sku})"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    attribute_value = models.ForeignKey(
        AttributeValue,
        related_name="images",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Img for {self.product.name}"

    class Meta:
        ordering = ["-is_main", "id"]
