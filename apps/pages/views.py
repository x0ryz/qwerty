from django.views.generic import TemplateView
from django.shortcuts import render
from django.db.models import Count, Min, Prefetch
from catalog.models import Product, ProductImage


class IndexView(TemplateView):
    template_name = 'pages/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['popular_products'] = Product.objects.annotate(
            orders=Count('variants__order_items'),
            min_price=Min('variants__price')
        ).prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.filter(
                is_main=True), to_attr='main_img_list')
        ).order_by('-orders')[:4]

        return context

class AboutView(TemplateView):
    template_name = "pages/about.html"