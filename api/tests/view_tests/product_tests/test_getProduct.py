from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Product
import colorama

class GetProductTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user('staffuser', 'staff@example.com', 'password123', is_staff=True)
        self.regular_user = User.objects.create_user('regularuser', 'regular@example.com', 'password123')
        self.visible_product = Product.objects.create(name="Visible Product", price=30.00, count_in_stock=10, visible=True)
        self.hidden_product = Product.objects.create(name="Hidden Product", price=40.00, count_in_stock=5, visible=False)

    def test_get_product_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse('product', kwargs={'pk': self.visible_product.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'Visible Product')

        response = self.client.get(reverse('product', kwargs={'pk': self.hidden_product.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'Hidden Product')

    def test_get_product_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('product', kwargs={'pk': self.visible_product.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'Visible Product')

        response = self.client.get(reverse('product', kwargs={'pk': self.hidden_product.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_product_non_existent(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse('product', kwargs={'pk': 999}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
