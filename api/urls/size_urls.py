from django.urls import path
from api.views import size_views as views

urlpatterns = [
    path("", views.getSizes, name="sizes"),
    path("create/", views.addSize, name="size-add"),
    path("delete/", views.removeSize, name="size-remove"),
]
