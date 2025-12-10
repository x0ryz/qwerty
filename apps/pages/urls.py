from django.urls import path
from . import views
from .views import AboutView, IndexView

app_name = "pages"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about"),
]