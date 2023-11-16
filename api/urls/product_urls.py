from django.urls import path
from api.views import product_views as views


urlpatterns = [
    path("", views.getProducts, name="products"),

    path("create/", views.createProduct, name="product-create"),

    path("<str:pk>/reviews/<str:review_id>/delete/", views.deleteProductReview, name="delete-review"),
    path("<str:pk>/reviews", views.createProductReview, name="create-review"),
    path("<str:pk>/", views.getProduct, name="product"),

    path("update/<str:pk>/", views.updateProduct, name="product-update"),
    path("delete/<str:pk>/", views.deleteProduct, name="product-delete"),


]