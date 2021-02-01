from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.error_404, name="index"),
    path("<uuid:token>", views.API.as_view(), name="api"),
    re_path(r".*", views.error_404),
]
