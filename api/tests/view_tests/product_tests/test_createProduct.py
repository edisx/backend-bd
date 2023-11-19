from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Product
import colorama

class CreateProductTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user('adminuser', 'admin@example.com', 'password123', is_staff=True, is_superuser=True)
        self.regular_user = User.objects.create_user('regularuser', 'regular@example.com', 'password123')

    def test_create_product_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "New Product", "price": 50, "count_in_stock": 15, "description": "A new test product"}
        response = self.client.post(reverse('product-create'), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.json()['name'], "product name")
        self.assertEqual(response.json()['price'], '0.00')
        self.assertEqual(response.json()['count_in_stock'], 0)
        self.assertEqual(response.json()['description'], "")

        self.assertTrue(Product.objects.filter(name="product name").exists())

    def test_create_product_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {"name": "New Product", "price": 50, "count_in_stock": 15, "description": "A new test product"}
        response = self.client.post(reverse('product-create'), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Product.objects.filter(name=data['name']).exists())

    def test_create_product_unauthenticated(self):
        data = {"name": "New Product", "price": 50, "count_in_stock": 15, "description": "A new test product"}
        response = self.client.post(reverse('product-create'), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Product.objects.filter(name=data['name']).exists())
