from django.contrib import admin
from .models import Product, ProductImage, Mesh, Color


# FIXME: move admin to some safe url later

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Mesh)
admin.site.register(Color)


