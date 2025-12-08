from django.urls import path
from . import views
from .views import AboutView

app_name = "pages"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", AboutView.as_view(), name="about"),
]