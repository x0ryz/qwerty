from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path(
        "category/<slug:category_slug>/",
        views.ProductListView.as_view(),
        name="product_list_by_category",
    ),
    path(
        "category/<slug:category_slug>/<slug:attr_slug>/<slug:value_slug>/",
        views.ProductListView.as_view(),
        name="product_list_by_attribute",
    ),
    path(
        "product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    path(
        "product/<slug:slug>/variant/",
        views.ProductVariantHTMXView.as_view(),
        name="product_variant_htmx",
    ),
]
