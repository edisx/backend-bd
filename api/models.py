from django.db import models
import uuid
from PIL import Image
import os
import trimesh

# Helper functions
def product_image_upload_path(instance, filename):
    return f'products/{uuid.uuid4()}.jpg'

def product_model_upload_path(instance, filename):
    return f'models/{uuid.uuid4()}{os.path.splitext(filename)[-1]}'

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    main_image = models.ImageField(upload_to=product_image_upload_path, null=True, blank=True)
    model_3d = models.FileField(upload_to=product_model_upload_path, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.model_3d:
            # Load the GLB file
            mesh = trimesh.load_mesh(self.model_3d.path)

            for name, geometry in mesh.geometry.items():
                Mesh.objects.get_or_create(product=self, name=name)

        if self.main_image:
            img = Image.open(self.main_image.path)
            if img.format != 'JPEG':
                img = img.convert('RGB')
                img.save(self.main_image.path, 'JPEG')

    def __str__(self):
        return self.name

# ProductImage Model
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_upload_path)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 
        
        # Open the saved image using PIL
        img = Image.open(self.image.path)
        
        # Convert to JPG if it's not
        if img.format != 'JPEG':
            img = img.convert('RGB')
            img.save(self.image.path, 'JPEG')

    def __str__(self):
        return f"Image for {self.product.name}"

# Mesh Model
class Mesh(models.Model):
    product = models.ForeignKey(Product, related_name='meshes', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)  # Name of the mesh as extracted from the .glb file

    def __str__(self):
        return f"Mesh {self.name} for {self.product.name}"

# Color Model
class Color(models.Model):
    mesh = models.ForeignKey(Mesh, related_name='colors', on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50)  # e.g. "saddlebrown"
    hex_code = models.CharField(max_length=7)  # e.g. "#8B4513"

    def __str__(self):
        return f"Color {self.color_name} ({self.hex_code}) for {self.mesh.name}"
