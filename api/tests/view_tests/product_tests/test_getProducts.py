from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Product
import colorama

class GetProductsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user('staffuser', 'staff@example.com', 'password123', is_staff=True)
        self.regular_user = User.objects.create_user('regularuser', 'regular@example.com', 'password123')

        self.visible_product = Product.objects.create(name="Visible Product", price=30.00, count_in_stock=10, visible=True)
        self.hidden_product = Product.objects.create(name="Hidden Product", price=40.00, count_in_stock=5, visible=False)

    def test_get_products_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('products'))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        # Adjusted to access the 'products' key
        self.assertTrue(any(item['name'] == 'Visible Product' for item in response_data['products']))

    def test_get_products_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse('products'))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        # Adjusted to access the 'products' key
        self.assertTrue(any(item['name'] == 'Visible Product' for item in response_data['products']))

    def test_get_products_unauthenticated(self):
        response = self.client.get(reverse('products'))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_pagination(self):
        for i in range(10):
            Product.objects.create(name=f"Product {i}", price=20.00, count_in_stock=5, visible=True)

        self.client.force_authenticate(user=self.regular_user)
        
        # Request the first page
        response = self.client.get(reverse('products'), {'page': 1})
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['products']), 4) 

        # Request the second page
        response = self.client.get(reverse('products'), {'page': 2})
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['products']), 4) 

