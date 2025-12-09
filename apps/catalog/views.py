import json
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Min, Prefetch
from django.core.paginator import Paginator

from .models import Category, Product, ProductImage, AttributeValue
from .filters import ProductFilter
from .recommender import Recommender
from cart.forms import CartAddProductForm


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product/list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        qs = Product.objects.all()

        category_slug = self.request.GET.get('category') or self.kwargs.get('category_slug')
        self.category = None

        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            qs = qs.filter(category=self.category)

        main_images = ProductImage.objects.filter(is_main=True)
        qs = qs.annotate(
            min_price=Min('variants__price'),
            orders_count=Count('variants__order_items')
        ).prefetch_related(
            Prefetch('images', queryset=main_images, to_attr='main_img_list')
        )

        self.filterset = ProductFilter(
            self.request.GET,
            queryset=qs,
            category=self.category
        )

        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        context['filter'] = self.filterset
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'variants__attributes__attribute',
            'images__attribute_value',
            'category',
            'brand',
            'keyboard_specs',
            'keycap_specs',
            'switch_specs'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        variants = product.variants.filter(available=True)

        attributes_map = {}
        for variant in variants:
            for attr_val in variant.attributes.all():
                attr_name = attr_val.attribute.name
                if attr_name not in attributes_map:
                    attributes_map[attr_name] = set()
                attributes_map[attr_name].add(attr_val)

        grouped_attributes = []
        for attr_name, values in attributes_map.items():
            grouped_attributes.append((attr_name, sorted(list(values), key=lambda x: x.id)))

        variants_js_map = {}
        for v in variants:
            attr_ids = sorted([str(av.id) for av in v.attributes.all()])
            key = "-".join(attr_ids)

            variants_js_map[key] = {
                'id': v.id,
                'price': float(v.price),
                'sku': v.sku,
                'stock': v.available
            }

        images_by_attr = {}
        general_images = list(product.images.filter(attribute_value__isnull=True))

        processed_values = set()
        for img in product.images.filter(attribute_value__isnull=False):
            val_id = img.attribute_value.id
            if val_id not in images_by_attr:
                images_by_attr[val_id] = []
            images_by_attr[val_id].append(img.image.url)
            processed_values.add(val_id)

        for val_id in images_by_attr:
            images_by_attr[val_id].extend([img.image.url for img in general_images])

        r = Recommender()
        recommended_products = r.suggest_products_for([product], 4)

        context.update({
            'cart_product_form': CartAddProductForm(),
            'grouped_attributes': grouped_attributes,
            'variants_json': json.dumps(variants_js_map),
            'images_by_attr': images_by_attr,
            'general_images': [img.image.url for img in general_images],
            'recommended_products': recommended_products
        })
        return context