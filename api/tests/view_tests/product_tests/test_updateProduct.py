from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Product, Category
import colorama

class UpdateProductTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user('adminuser', 'admin@example.com', 'password123', is_staff=True, is_superuser=True)
        self.regular_user = User.objects.create_user('regularuser', 'regular@example.com', 'password123')
        self.product = Product.objects.create(name="Test Product", price=30.00, count_in_stock=10, description="A test product", visible=True)
        self.category = Category.objects.create(name="Test Category")

    def test_update_product_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "Updated Product", "price": 35.00, "count_in_stock": 5, "description": "An updated test product", "visible": False}
        response = self.client.put(reverse('product-update', kwargs={'pk': self.product.id}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, data['name'])
        self.assertEqual(self.product.description, data['description'])
        self.assertEqual(self.product.visible, data['visible'])

    def test_update_product_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {"name": "Updated Product", "price": 35.00}
        response = self.client.put(reverse('product-update', kwargs={'pk': self.product.id}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_product(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"price": 40.00}
        response = self.client.put(reverse('product-update', kwargs={'pk': self.product.id}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, data['price'])

    def test_update_product_with_invalid_category(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"category": "999"}
        response = self.client.put(reverse('product-update', kwargs={'pk': self.product.id}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_product(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "Updated Product", "price": 35.00}
        response = self.client.put(reverse('product-update', kwargs={'pk': 999}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
