from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Order, ShippingAddress
from datetime import datetime
import colorama

class UpdateOrderToPaidTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create two users
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'user123')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'user456')

        # Create an order for user1
        self.order = Order.objects.create(user=self.user1, total_price=100.0)
        ShippingAddress.objects.create(order=self.order, address="123 Test St", city="Test City", postal_code="12345", country="Testland")

    def test_update_order_to_paid_success(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(reverse('pay', kwargs={'pk': self.order.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.order.refresh_from_db() 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.order.is_paid)
        self.assertIsNotNone(self.order.paid_at)
        self.assertIsInstance(self.order.paid_at, datetime)

    def test_update_nonexistent_order(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(reverse('pay', kwargs={'pk': 999}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_unauthorized(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(reverse('pay', kwargs={'pk': self.order.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 


