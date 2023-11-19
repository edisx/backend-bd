from django.contrib import admin
from .models import Category, Product, ProductImage, Mesh, Color, Review, Order, OrderItem, ShippingAddress, ShoeSize


# FIXME: move admin to some safe url later

admin.site.register(Category)

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Mesh)
admin.site.register(Color)
admin.site.register(ShoeSize)

admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)



