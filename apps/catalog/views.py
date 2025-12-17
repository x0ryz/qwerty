from string import printable

from cart.forms import CartAddProductForm
from django.core.paginator import Paginator
from django.db.models import Count, Min, Prefetch
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, View

from .filters import ProductFilter
from .models import Attribute, AttributeValue, Category, Product, ProductImage
from .recommender import Recommender


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self):
        qs = Product.objects.all()

        category_slug = self.request.GET.get("category") or self.kwargs.get(
            "category_slug"
        )
        self.category = None

        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            qs = qs.filter(category=self.category)

        self.target_attribute = None
        self.target_value = None

        attr_slug = self.kwargs.get("attr_slug")
        value_slug = self.kwargs.get("value_slug")

        if attr_slug and value_slug:
            self.target_attribute = get_object_or_404(Attribute, slug=attr_slug)
            self.target_value = get_object_or_404(
                AttributeValue, slug=value_slug, attribute=self.target_attribute
            )

            # Фільтруємо QuerySet
            qs = qs.filter(
                attributes__attribute=self.target_attribute,
                attributes=self.target_value,
            )

        # 3. Анотації та префетч (без змін)
        images_qs = ProductImage.objects.order_by("sort_order")

        qs = qs.annotate(
            min_price=Min("variants__price"),
            orders_count=Count("variants__order_items"),
        ).prefetch_related(
            Prefetch("images", queryset=images_qs, to_attr="main_img_list")
        )

        # 4. Django Filter (без змін - він працюватиме поверх відфільтрованого списку)
        self.filterset = ProductFilter(
            self.request.GET, queryset=qs, category=self.category
        )

        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["category"] = self.category
        context["categories"] = Category.objects.all()
        context["filter"] = self.filterset

        # Додаємо атрибути в контекст, щоб вивести в шаблоні (наприклад: "Layout: 75%")
        context["current_attribute"] = self.target_attribute
        context["current_value"] = self.target_value

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "brand")
            .prefetch_related("images", "variants__attributes__attribute")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        variants = self.object.variants.prefetch_related("attributes__attribute").all()

        default_variant = variants.first()
        context["default_variant"] = default_variant

        # Create a set of Attribute IDs belonging to the default variant.
        # We pass this to the template to mark the correct radio buttons as 'checked'.
        if default_variant:
            selected_ids = set(default_variant.attributes.values_list("id", flat=True))
        else:
            selected_ids = set()

        context["selected_attr_ids"] = selected_ids

        context["cart_product_form"] = CartAddProductForm()

        # Logic to extract unique attribute options for UI selectors (buttons).
        # We iterate through all variants and collect unique (attribute_id, value) pairs
        # to ensure we don't display duplicate buttons (e.g., multiple "Red" or "Ionic White").
        seen = set()
        unique_attrs = []

        for variant in variants:
            for attr in variant.attributes.all():
                # Use a composite key to identify uniqueness
                key = (attr.attribute_id, attr.value)
                if key not in seen:
                    seen.add(key)
                    unique_attrs.append(attr)

        unique_attrs.sort(key=lambda x: (x.attribute.id, x.id))
        context["attribute_values"] = unique_attrs

        return context


class ProductVariantHTMXView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        filters = request.GET.dict()

        variants = product.variants.all()

        # Iteratively filter variants based on ALL selected attributes (AND logic).
        # Assumes that request.GET contains pairs like ?color=Ionic%20White&profile-switch=Brown.
        for attr, value in filters.items():
            variants = variants.filter(
                attributes__attribute__slug=attr,
                attributes__value=value,
            )

        variant = variants.first()

        return render(
            request,
            "catalog/_variant_info.html",
            {"variant": variant, "cart_product_form": CartAddProductForm()},
        )
