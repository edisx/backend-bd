from django.urls import path
from api.views import category_views as views


urlpatterns = [
    path("", views.getCategories, name="categories"),
    path("create/", views.createCategory, name="category-create"),
    path("update/<str:pk>/", views.updateCategory, name="category-update"),
    path("delete/<str:pk>/", views.deleteCategory, name="category-delete"),

]