from django.urls import path
from api.views import product_views as views

urlpatterns = [
    path("", views.getProducts, name="products"),
]