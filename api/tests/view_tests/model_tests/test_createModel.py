from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Product, User
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.conf import settings
import colorama

class CreateModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.client.force_authenticate(user=self.admin_user)
        self.product = Product.objects.create(name="Test Product", price=10.99)

    def test_create_model_success(self):
        # Path to the 3D model file
        test_model_path = os.path.join(settings.BASE_DIR, 'api', 'tests', 'test_files', 'sample_model.glb')

        with open(test_model_path, 'rb') as model_file:
            data = {
                'product_id': self.product.id,
                'model_3d': SimpleUploadedFile(name='sample_model.glb', content=model_file.read(), content_type='application/octet-stream')
            }
            response = self.client.post(reverse('model-create'), data, format='multipart')
            print(colorama.Fore.MAGENTA + "Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertTrue(self.product.model_3d)

    def test_create_model_no_product_id(self):
        test_model_path = os.path.join(settings.BASE_DIR, 'api', 'tests', 'test_files', 'sample_model.glb')
        with open(test_model_path, 'rb') as model_file:
            data = {
                'model_3d': SimpleUploadedFile(name='sample_model.glb', content=model_file.read(), content_type='application/octet-stream')
            }
            response = self.client.post(reverse('model-create'), data, format='multipart')
            print(colorama.Fore.MAGENTA + "Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_model_product_not_found(self):
        test_model_path = os.path.join(settings.BASE_DIR, 'api', 'tests', 'test_files', 'sample_model.glb')
        with open(test_model_path, 'rb') as model_file:
            data = {
                'product_id': 999,
                'model_3d': SimpleUploadedFile(name='sample_model.glb', content=model_file.read(), content_type='application/octet-stream')
            }
            response = self.client.post(reverse('model-create'), data, format='multipart')
            print(colorama.Fore.MAGENTA + "Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_model_no_model_file(self):
        data = {
            'product_id': self.product.id
        }
        response = self.client.post(reverse('model-create'), data, format='multipart')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
