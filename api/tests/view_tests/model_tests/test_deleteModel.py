from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Product, User, Mesh
import os
from django.conf import settings

class DeleteModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.client.force_authenticate(user=self.admin_user)
        self.product = Product.objects.create(name="Test Product", price=10.99)

        # Simulating the creation of meshes when a model is uploaded
        self.mesh1 = Mesh.objects.create(product=self.product, name="Mesh1")
        self.mesh2 = Mesh.objects.create(product=self.product, name="Mesh2")

    def test_delete_model_success(self):
        response = self.client.delete(reverse('model-delete', kwargs={'pk': self.product.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        updated_product = Product.objects.get(id=self.product.id)
        self.assertFalse(updated_product.model_3d)
        self.assertFalse(Mesh.objects.filter(product=self.product).exists())


    def test_delete_model_nonexistent_product(self):
        response = self.client.delete(reverse('model-delete', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_model_permission_denied(self):
        self.client.force_authenticate(user=User.objects.create_user('user', 'user@example.com', 'user123'))
        response = self.client.delete(reverse('model-delete', kwargs={'pk': self.product.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    