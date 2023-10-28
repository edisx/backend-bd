from django.db import models
from django.contrib.auth.models import User
import uuid
from PIL import Image
import os
import trimesh
from django.conf import settings


# Helper functions
def product_image_upload_path(instance, filename):
    return f"products/{uuid.uuid4()}.jpg"


def product_model_upload_path(instance, filename):
    return f"models/{uuid.uuid4()}{os.path.splitext(filename)[-1]}"


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# ShoeSize Model
class ShoeSize(models.Model):
    size = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.size)


# Product Model
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )
    description = models.TextField(null=True, blank=True)
    sizes = models.ManyToManyField(ShoeSize, blank=True, related_name='products')
    rating = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    num_reviews = models.IntegerField(null=True, blank=True, default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    count_in_stock = models.IntegerField(null=True, blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    model_3d = models.FileField(
        upload_to=product_model_upload_path, null=True, blank=True
    )
    visible = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.model_3d:
            # Delete all meshes associated with this product
            Mesh.objects.filter(product=self).delete()

            # Load the GLB file
            mesh = trimesh.load_mesh(self.model_3d.path)

            # dont delete this "geometry" key
            for name, geometry in mesh.geometry.items():
                Mesh.objects.get_or_create(product=self, name=name)

    def delete(self, *args, **kwargs):
        # Check if there is a model associated and delete the file before deleting the instance
        if self.model_3d:
            file_path = os.path.join(settings.MEDIA_ROOT, self.model_3d.path)
            if os.path.exists(file_path):
                os.remove(file_path)

        for img in self.images.all():
            img.delete()

        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


# ProductImage Model
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=product_image_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Open the saved image using PIL
        img = Image.open(self.image.path)

        # Convert to JPG if it's not
        if img.format != "JPEG":
            img = img.convert("RGB")
            img.save(self.image.path, "JPEG")

    def delete(self, *args, **kwargs):
        if self.image:
            file_path = os.path.join(settings.MEDIA_ROOT, self.image.path)
            if os.path.exists(file_path):
                os.remove(file_path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"


# Mesh Model
class Mesh(models.Model):
    product = models.ForeignKey(
        Product, related_name="meshes", on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=200
    )  # Name of the mesh as extracted from the .glb file
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mesh {self.name} for {self.product.name}"


# Color Model
class Color(models.Model):
    mesh = models.ForeignKey(Mesh, related_name="colors", on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50)  # e.g. "saddlebrown"
    hex_code = models.CharField(max_length=7)  # e.g. "#8B4513"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Color {self.color_name} ({self.hex_code}) for {self.mesh.name}"


# Review
class Review(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True, default=0)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"


# Order
class Order(models.Model):
    user = models.ForeignKey(User, related_name="orders", on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=200, null=True, blank=True)
    tax_price = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    shipping_price = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    total_price = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"


# OrderItem
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True, default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    image = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem {self.id} for {self.order.id}"


# ShippingAddress
class ShippingAddress(models.Model):
    order = models.OneToOneField(
        Order, related_name="shipping_address", on_delete=models.CASCADE
    )
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    shipping_price = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ShippingAddress for {self.order.id}"
