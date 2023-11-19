from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Order, ShippingAddress
import colorama


class GetMyOrdersTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user("user1", "user1@example.com", "user123")
        self.user2 = User.objects.create_user("user2", "user2@example.com", "user456")

        self.order1 = Order.objects.create(user=self.user1, total_price=100.0)
        ShippingAddress.objects.create(
            order=self.order1,
            address="123 Main St",
            city="City1",
            postal_code="12345",
            country="Country1",
        )

        self.order2 = Order.objects.create(user=self.user1, total_price=200.0)
        ShippingAddress.objects.create(
            order=self.order2,
            address="456 Main St",
            city="City2",
            postal_code="67890",
            country="Country2",
        )

        self.order3 = Order.objects.create(user=self.user2, total_price=300.0)
        ShippingAddress.objects.create(
            order=self.order3,
            address="789 Main St",
            city="City3",
            postal_code="101112",
            country="Country3",
        )

    def test_get_my_orders_success(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse("myorders"))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_my_orders_no_orders(self):
        new_user = User.objects.create_user("user3", "user3@example.com", "user789")
        self.client.force_authenticate(user=new_user)
        response = self.client.get(reverse("myorders"))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_my_orders_unauthorized(self):
        response = self.client.get(reverse("myorders"))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_access_others_orders(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse("myorders"))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertNotIn(self.order1.id, [order["id"] for order in response.data])
