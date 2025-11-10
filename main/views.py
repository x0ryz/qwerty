from django.views import generic
from .models import Product, Category, Model

class CatalogView(generic.ListView):
    model = Product
    template_name = "main/product/catalog.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slugs = self.request.GET.getlist('category')
        model_names = self.request.GET.getlist('model')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if category_slugs: 
            queryset = queryset.filter(category__slug__in=category_slugs)

        if model_names:
            queryset = queryset.filter(model__name__in=model_names)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['models'] = Model.objects.all()
        return context
