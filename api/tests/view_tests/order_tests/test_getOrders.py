from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Order, ShippingAddress
import colorama


class GetOrdersTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create admin and regular users
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.user = User.objects.create_user('user', 'user@example.com', 'user123')

        order1 = Order.objects.create(user=self.admin_user, total_price=100.0)
        ShippingAddress.objects.create(order=order1, address="123 Test St", city="Test City", postal_code="12345", country="Testland")

        order2 = Order.objects.create(user=self.user, total_price=200.0)
        ShippingAddress.objects.create(order=order2, address="456 Test Ave", city="Testville", postal_code="67890", country="Testland")

    def test_get_all_orders_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('orders'))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_all_orders_denied_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('orders'))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

