from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Order, ShippingAddress
from django.utils import timezone
import colorama

class ResetOrderToUndeliveredTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create admin and regular users
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.regular_user = User.objects.create_user('user', 'user@example.com', 'user123')

        # Create an order and set it to delivered
        self.order = Order.objects.create(user=self.regular_user, total_price=100.0, is_delivered=True, delivered_at=timezone.now())
        ShippingAddress.objects.create(order=self.order, address="123 Test St", city="Test City", postal_code="12345", country="Testland")

    def test_reset_order_to_undelivered_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(reverse('order-undelivered', kwargs={'pk': self.order.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.order.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.order.is_delivered)
        self.assertIsNone(self.order.delivered_at)

    def test_reset_order_to_undelivered_non_admin(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.put(reverse('order-undelivered', kwargs={'pk': self.order.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reset_nonexistent_order_to_undelivered(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(reverse('order-undelivered', kwargs={'pk': 999}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
