from django.urls import path
from django.views.generic import TemplateView

from .views import *

app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("page/<path:menu_path>/", PageView.as_view(), name="page"),
    path("page/", PageView.as_view(), name="page-base"),
]

