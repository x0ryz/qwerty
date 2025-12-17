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
    attributes = models.ManyToManyField(
        AttributeValue, related_name="products", blank=True
    )
    description = models.TextField(blank=True)
    specs = models.JSONField(default=dict, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])

    def get_main_image_url(self):
        images = self.images.all()

        if not images:
            return None

        main_img = sorted(images, key=lambda x: x.sort_order)[0]
        return main_img.image.url

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
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.available = False
        super().save(*args, **kwargs)

    def get_images(self):
        variant_attr_ids = {a.id for a in self.attributes.all()}

        all_product_images = self.product.images.all()

        specific_images = [
            img
            for img in all_product_images
            if img.attribute_value_id in variant_attr_ids
        ]

        if specific_images:
            return sorted(specific_images, key=lambda x: x.sort_order)

        return sorted(all_product_images, key=lambda x: x.sort_order)

    def get_image_url(self):
        """
        Повертає URL головного зображення саме для цього варіанту.
        """
        images = self.get_images()
        if images:
            return images[0].image.url
        return None

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
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Img for {self.product.name}"
