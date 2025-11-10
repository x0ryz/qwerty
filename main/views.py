from django.views import generic

class CatalogView(generic.TemplateView):
    template_name = "main/product/catalog.html"
