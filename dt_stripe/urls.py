from django.urls import path
from django.views.generic import TemplateView

from .views import *

app_name = "dt-stripe"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("customers", CustomerListView.as_view(), name="customer-list"),
    path("customers/create", CustomerCreateView.as_view(), name="customer-create"),
    path(
        "customers/<int:customer_id>",
        CustomerDetailView.as_view(),
        name="customer-detail",
    ),
    path("products", ProductListView.as_view(), name="product-list"),
    path("products/create", ProductCreateView.as_view(), name="product-create"),
    path("plans", PlanListView.as_view(), name="plan-list"),
    path("plans/create", PlanCreateView.as_view(), name="plan-create"),
    path("skus", SKUListView.as_view(), name="sku-list"),
    path("skus/create", SKUCreateView.as_view(), name="sku-create"),
]
