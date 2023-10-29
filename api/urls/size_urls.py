from django.urls import path
from api.views import size_views as views

urlpatterns = [
    path("", views.getSizes, name="sizes"),
    path("update/", views.updateProductSizes, name="sizes-update"),

]
