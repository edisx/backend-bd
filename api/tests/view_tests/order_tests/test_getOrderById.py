from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Order, ShippingAddress
import colorama

class GetOrderByIdTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'user123')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'user456')

        # Create orders and shipping addresses
        self.order1 = Order.objects.create(user=self.user1, total_price=100.0)
        ShippingAddress.objects.create(order=self.order1, address="123 Test St", city="Test City", postal_code="12345", country="Testland")

        self.order2 = Order.objects.create(user=self.user2, total_price=200.0)
        ShippingAddress.objects.create(order=self.order2, address="456 Test Ave", city="Testville", postal_code="67890", country="Testland")

    def test_get_order_by_id_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('user-order', args=[self.order1.id]))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order1.id)

    def test_get_own_order_regular_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('user-order', args=[self.order1.id]))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order1.id)

    def test_get_other_user_order_regular_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('user-order', args=[self.order2.id]))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_non_existent_order(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('user-order', args=[999]))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

