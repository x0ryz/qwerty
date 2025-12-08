from django.shortcuts import get_object_or_404, render

from cart.forms import CartAddProductForm

from .models import Category, Product, ProductImage
from django.db.models import Count, Min, Prefetch
from .recommender import Recommender


def product_list(request):
    category = None
    categories = Category.objects.all()
    products = Product.objects.annotate(orders=Count('order_items'), min_price=Min('variants__price')).prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.filter(is_main=True), to_attr='main_img_list')).order_by('-orders')[:4]
    return render(
        request,
        "catalog/product/list.html",
        {"category": category, "categories": categories, "products": products},
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart_product_form = CartAddProductForm()
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)
    return render(
        request,
        "catalog/product/detail.html",
        {"product": product, "cart_product_form": cart_product_form, 'recommended_products': recommended_products},
    )
