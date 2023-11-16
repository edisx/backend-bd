from django.urls import path
from api.views import model_views as views

urlpatterns = [
    path("create/", views.createModel, name="model-create"),
    path("delete/<str:pk>/", views.deleteModel, name="model-delete"),

    path("color/create/", views.addColor, name="color-create"),
    path("color/create-multiple/", views.addColors, name="colors-create-multiple"),
    path("color/update/<str:pk>/", views.updateColor, name="color-update"),
    path("color/delete/<str:pk>/", views.deleteColor, name="color-delete"),
]