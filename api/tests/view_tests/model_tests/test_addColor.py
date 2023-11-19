from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Mesh, Product, User, Color
import os
import colorama

class AddColorTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin and a regular user
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.regular_user = User.objects.create_user('user', 'user@example.com', 'user123')

        # Create a test product and mesh
        self.product = Product.objects.create(name="Test Product", price=10.99)
        self.mesh = Mesh.objects.create(product=self.product, name="Mesh1")

    def test_add_color_success(self):
        self.client.force_authenticate(user=self.admin_user)
        color_data = {'mesh_id': self.mesh.id, 'color_name': 'Red', 'hex_code': '#FF0000'}
        response = self.client.post(reverse('color-create'), color_data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Color.objects.filter(mesh=self.mesh, color_name='Red').exists())

    def test_add_color_invalid_data(self):
        self.client.force_authenticate(user=self.admin_user)
        incomplete_data = {'mesh_id': self.mesh.id, 'color_name': 'Blue'}
        response = self.client.post(reverse('color-create'), incomplete_data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_color_permission_denied(self):
        self.client.force_authenticate(user=self.regular_user)
        color_data = {'mesh_id': self.mesh.id, 'color_name': 'Green', 'hex_code': '#008000'}
        response = self.client.post(reverse('color-create'), color_data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_color_duplicate(self):
        self.client.force_authenticate(user=self.admin_user)
        Color.objects.create(mesh=self.mesh, color_name='Yellow', hex_code='#FFFF00')
        duplicate_data = {'mesh_id': self.mesh.id, 'color_name': 'Yellow', 'hex_code': '#FFFF00'}
        response = self.client.post(reverse('color-create'), duplicate_data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

