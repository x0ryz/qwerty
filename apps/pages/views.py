from catalog.models import Product, ProductImage
from django.db.models import Count, Min, Prefetch
from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        images_qs = ProductImage.objects.order_by("sort_order")

        base_qs = Product.objects.annotate(
            min_price=Min("variants__price")
        ).prefetch_related(
            Prefetch("images", queryset=images_qs, to_attr="main_img_list")
        )

        context["popular_products"] = base_qs.annotate(
            orders=Count("variants__order_items")
        ).order_by("-orders")[:4]

        context["new_arrivals"] = base_qs.order_by("-created")[:4]

        return context


class AboutView(TemplateView):
    template_name = "pages/about.html"
