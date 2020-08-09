from django.urls import path
from django.views.generic import TemplateView

from .views import *

app_name = "simple-sendgrid"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("test", TestView.as_view(), name="test"),
]
