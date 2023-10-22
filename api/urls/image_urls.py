from django.urls import path
from api.views import image_views as views


urlpatterns = [
    path("create/", views.createImage, name="image-create"),
    path("delete/<str:pk>/", views.deleteImage, name="image-update"),
]