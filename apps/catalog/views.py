from django.shortcuts import get_object_or_404, render

from cart.forms import CartAddProductForm

from .models import Category, Product, ProductImage
from django.core.paginator import Paginator
from .filters import ProductFilter
from django.db.models import Count, Min, Prefetch
from .recommender import Recommender

import json


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()

    products_qs = Product.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products_qs = products_qs.filter(category=category)

    product_filter = ProductFilter(request.GET, queryset=products_qs)

    filtered_qs = product_filter.qs.distinct()

    main_images = ProductImage.objects.filter(is_main=True)

    products = filtered_qs.annotate(
        min_price=Min('variants__price'),
        orders=Count('order_items')
    ).prefetch_related(
        Prefetch('images', queryset=main_images, to_attr='main_img_list')
    )

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog/product/list.html', {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'filter': product_filter,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related('variants__color', 'variants__switch', 'images__color'),
        slug=slug
    )

    variants = product.variants.filter(available=True)

    available_colors = sorted(list({v.color for v in variants}), key=lambda c: c.id)
    available_switches = sorted(list({v.switch for v in variants if v.switch}), key=lambda s: s.id)

    variants_map = {}
    for v in variants:
        switch_id = v.switch.id if v.switch else 'none'
        key = f"{v.color.id}-{switch_id}"

        variants_map[key] = {
            'id': v.id,
            'price': float(v.price),
            'sku': v.sku,
            'stock': v.available,
        }

    images_by_color = {}

    general_images = product.images.filter(color__isnull=True)

    for color in available_colors:
        color_imgs = list(general_images) + list(product.images.filter(color=color))
        images_by_color[color.id] = color_imgs

    cart_product_form = CartAddProductForm()
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)

    return render(
        request,
        "catalog/product/detail.html",
        {"product": product, "cart_product_form": cart_product_form, 'recommended_products': recommended_products,
         "available_colors": available_colors,
         "available_switches": available_switches,
         "variants_json": json.dumps(variants_map),
         "images_by_color": images_by_color,
         },
    )
