from django.views.generic import TemplateView
from django.shortcuts import render
from django.db.models import Count
from catalog.models import Product

def index(request):
    products = Product.objects.annotate(orders=Count('order_items')).order_by('-orders')[:4]

    return render(request, 'pages/index.html', {'products': products})

class AboutView(TemplateView):
    template_name = "pages/about.html"