from django.views.generic import TemplateView
from django.shortcuts import render
from django.db.models import Count, Min, Prefetch
from catalog.models import Product, ProductImage


def index(request):
    main_images = ProductImage.objects.filter(is_main=True)
    products = Product.objects.annotate(orders=Count('order_items'), min_price=Min('variants__price')).prefetch_related(Prefetch('images', queryset=main_images, to_attr='main_img_list')).order_by('-orders')[:4]
    return render(request, 'pages/index.html', {'products': products})

class AboutView(TemplateView):
    template_name = "pages/about.html"