from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Mesh, Product, User, Color
import os

class DeleteColorTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin and a regular user
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.regular_user = User.objects.create_user('user', 'user@example.com', 'user123')
        
        # Create a test product, mesh, and color
        self.product = Product.objects.create(name="Test Product", price=10.99)
        self.mesh = Mesh.objects.create(product=self.product, name="Mesh1")
        self.color = Color.objects.create(mesh=self.mesh, color_name='Blue', hex_code='#0000FF')

    def test_delete_color_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('color-delete', kwargs={'pk': self.color.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Color.objects.filter(id=self.color.id).exists())

    def test_delete_color_nonexistent(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('color-delete', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_color_permission_denied(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(reverse('color-delete', kwargs={'pk': self.color.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)