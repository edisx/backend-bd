from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Product, ProductImage, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os


class CreateImageTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            "admin", "admin@example.com", "admin123"
        )
        self.client.force_authenticate(user=self.admin_user)
        self.product = Product.objects.create(name="Test Product", price=10.99)

    def test_create_image_success(self):
        test_image_path = os.path.join(settings.BASE_DIR, 'api', 'tests', 'test_files', 'sample_image.jpg')
        
        with open(test_image_path, 'rb') as img_file:
            image_data = {
                "product_id": self.product.id,
                "image": SimpleUploadedFile(name='test_image.jpg', content=img_file.read(), content_type='image/jpeg')
            }
            response = self.client.post(reverse('image-create'), image_data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProductImage.objects.filter(product=self.product).exists())

    def test_create_image_for_nonexistent_product(self):
        image_data = {
            "product_id": 999,
            "image": SimpleUploadedFile(
                name="test_image.jpg", content=b"", content_type="image/jpeg"
            ),
        }
        response = self.client.post(
            reverse("image-create"), image_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_image_without_product_id(self):
        image_data = {
            "image": SimpleUploadedFile(
                name="test_image.jpg", content=b"", content_type="image/jpeg"
            ),
        }
        response = self.client.post(
            reverse("image-create"), image_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_create_image_without_image(self):
        image_data = {"product_id": self.product.id}
        response = self.client.post(
            reverse("image-create"), image_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_create_image_without_authentication(self):
        self.client.force_authenticate(user=None)
        image_data = {
            "product_id": self.product.id,
            "image": SimpleUploadedFile(
                name="test_image.jpg", content=b"", content_type="image/jpeg"
            ),
        }
        response = self.client.post(
            reverse("image-create"), image_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    

