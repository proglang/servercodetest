from django.urls import path, re_path
from . import views

urlpatterns = [
    path("<uuid:token>", views.API.as_view(), name="index"),
    re_path(r".*", views.error_404),
]
