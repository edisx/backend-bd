from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Product, ProductImage, User
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.conf import settings

class DeleteImageTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a test admin user
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.client.force_authenticate(user=self.admin_user)

        # Create a test product and image
        self.product = Product.objects.create(name="Test Product", price=10.99)
        test_image_path = os.path.join(settings.BASE_DIR, 'api', 'tests', 'test_files', 'sample_image.jpg')
        with open(test_image_path, 'rb') as img_file:
            self.image = ProductImage.objects.create(
                product=self.product,
                image=SimpleUploadedFile(name='test_image.jpg', content=img_file.read(), content_type='image/jpeg')
            )

    def test_delete_image_success(self):
        response = self.client.delete(reverse('image-delete', kwargs={'pk': self.image.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProductImage.objects.filter(id=self.image.id).exists())

    def test_delete_nonexistent_image(self):
        response = self.client.delete(reverse('image-delete', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_image_without_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(reverse('image-delete', kwargs={'pk': self.image.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_product_cascade(self):
        response = self.client.delete(reverse('product-delete', kwargs={'pk': self.product.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProductImage.objects.filter(id=self.image.id).exists())
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
                                                  

