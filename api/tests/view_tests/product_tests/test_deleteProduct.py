from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Product
import colorama

class DeleteProductTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user('adminuser', 'admin@example.com', 'password123', is_staff=True, is_superuser=True)
        self.regular_user = User.objects.create_user('regularuser', 'regular@example.com', 'password123')
        self.product = Product.objects.create(name="Test Product", price=30.00, count_in_stock=10, visible=True)

    def test_delete_product_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('product-delete', kwargs={'pk': self.product.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=self.product.id)

    def test_delete_product_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(reverse('product-delete', kwargs={'pk': self.product.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIsNotNone(Product.objects.get(id=self.product.id))

    def test_delete_product_unauthenticated(self):
        response = self.client.delete(reverse('product-delete', kwargs={'pk': self.product.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_nonexistent_product(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('product-delete', kwargs={'pk': 999}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
