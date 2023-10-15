from django.contrib import admin
from .models import Product, ProductImage


# FIXME: move admin to some safe url later

admin.site.register(Product)
admin.site.register(ProductImage)


