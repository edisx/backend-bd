from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Mesh, Product, User, Color
import os
import colorama

class UpdateColorTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin and a regular user
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.regular_user = User.objects.create_user('user', 'user@example.com', 'user123')
        
        # Create a test product, mesh, and color
        self.product = Product.objects.create(name="Test Product", price=10.99)
        self.mesh = Mesh.objects.create(product=self.product, name="Mesh1")
        self.color = Color.objects.create(mesh=self.mesh, color_name='Blue', hex_code='#0000FF')

    def test_update_color_success(self):
        self.client.force_authenticate(user=self.admin_user)
        updated_data = {'color_name': 'Green', 'hex_code': '#008000'}
        response = self.client.put(reverse('color-update', kwargs={'pk': self.color.id}), updated_data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.color.refresh_from_db()
        self.assertEqual(self.color.color_name, 'Green')
        self.assertEqual(self.color.hex_code, '#008000')

    def test_update_color_invalid_data(self):
        self.client.force_authenticate(user=self.admin_user)
        incomplete_data = {'color_name': 'Red'}
        response = self.client.put(reverse('color-update', kwargs={'pk': self.color.id}), incomplete_data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_color_permission_denied(self):
        self.client.force_authenticate(user=self.regular_user)
        updated_data = {'color_name': 'Yellow', 'hex_code': '#FFFF00'}
        response = self.client.put(reverse('color-update', kwargs={'pk': self.color.id}), updated_data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_color(self):
        self.client.force_authenticate(user=self.admin_user)
        updated_data = {'color_name': 'Purple', 'hex_code': '#800080'}
        response = self.client.put(reverse('color-update', kwargs={'pk': 999}), updated_data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)