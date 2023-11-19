from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Product, ShoeSize, Order, ShippingAddress, OrderItem
import colorama

class AddOrderTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password123')
        self.product1 = Product.objects.create(name="Test Product 1", price=10.00, count_in_stock=5)
        self.product2 = Product.objects.create(name="Test Product 2", price=20.00, count_in_stock=10)

        size, created = ShoeSize.objects.get_or_create(size=42)
        self.shoe_size = size


    def test_add_order_success(self):
        self.client.force_authenticate(user=self.user)
        order_data = {
            "orderItems": [
                {"product": self.product1.id, "name": "Test Product 1", "price": 10.00, "image": "image_url", "size": {"id": self.shoe_size.id}, "colors": {}},
                {"product": self.product2.id, "name": "Test Product 2", "price": 20.00, "image": "image_url", "size": {"id": self.shoe_size.id}, "colors": {}}
            ],
            "paymentMethod": "PayPal",
            "taxPrice": 5.00,
            "shippingPrice": 2.00,
            "totalPrice": 37.00,
            "shippingAddress": {
                "address": "123 Test St",
                "city": "Test City",
                "postalCode": "12345",
                "country": "Testland"
            }
        }
        response = self.client.post(reverse('orders-add'), order_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_add_order_no_order_items(self):
        self.client.force_authenticate(user=self.user)
        order_data = {
            "paymentMethod": "PayPal",
            "taxPrice": 5.00,
            "shippingPrice": 2.00,
            "totalPrice": 37.00,
            "shippingAddress": {
                "address": "123 Test St",
                "city": "Test City",
                "postalCode": "12345",
                "country": "Testland"
            }
        }
        response = self.client.post(reverse('orders-add'), order_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_order_with_nonexistent_product(self):
        self.client.force_authenticate(user=self.user)
        order_data = {
            "orderItems": [
                {"product": 9999, "name": "Nonexistent Product", "price": 10.00, "image": "image_url", "size": {"id": self.shoe_size.id}, "colors": {}}
            ],
            "paymentMethod": "PayPal",
            "taxPrice": 5.00,
            "shippingPrice": 2.00,
            "totalPrice": 37.00,
            "shippingAddress": {
                "address": "123 Test St",
                "city": "Test City",
                "postalCode": "12345",
                "country": "Testland"
            }
        }
        response = self.client.post(reverse('orders-add'), order_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_order_insufficient_stock(self):
        self.client.force_authenticate(user=self.user)
        # Create a product with zero stock
        out_of_stock_product = Product.objects.create(name="Out of Stock Product", price=30.00, count_in_stock=0)

        order_data = {
            "orderItems": [
                {"product": out_of_stock_product.id, "name": "Out of Stock Product", "price": 30.00, "image": "image_url", "size": {"id": self.shoe_size.id}, "colors": {}}
            ],
            "paymentMethod": "PayPal",
            "taxPrice": 5.00,
            "shippingPrice": 2.00,
            "totalPrice": 37.00,
            "shippingAddress": {
                "address": "123 Test St",
                "city": "Test City",
                "postalCode": "12345",
                "country": "Testland"
            }
        }
        response = self.client.post(reverse('orders-add'), order_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_add_order_missing_required_fields(self):
        self.client.force_authenticate(user=self.user)
        order_data = {
            "paymentMethod": "PayPal",
            "taxPrice": 5.00,
            "shippingPrice": 2.00,
            "totalPrice": 37.00
        }
        response = self.client.post(reverse('orders-add'), order_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    

