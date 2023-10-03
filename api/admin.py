from django.contrib import admin
from .models import Product


# FIXME: move admin to some safe url later

admin.site.register(Product)


