from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Product, Review
import colorama

class CreateProductReviewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password123')
        self.product = Product.objects.create(name="Test Product", price=30.00, count_in_stock=10)

    def test_create_review(self):
        self.client.force_authenticate(user=self.user)
        data = {"rating": 5, "comment": "Great product"}
        response = self.client.post(reverse('create-review', kwargs={'pk': self.product.id}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_review_nonexistent_product(self):
        self.client.force_authenticate(user=self.user)
        data = {"rating": 5, "comment": "Great product"}
        response = self.client.post(reverse('create-review', kwargs={'pk': 999}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_review(self):
        self.client.force_authenticate(user=self.user)
        Review.objects.create(user=self.user, product=self.product, rating=4, comment="Good product")
        data = {"rating": 5, "comment": "Another comment"}
        response = self.client.post(reverse('create-review', kwargs={'pk': self.product.id}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_without_rating(self):
        self.client.force_authenticate(user=self.user)
        data = {"comment": "Nice product"}
        response = self.client.post(reverse('create-review', kwargs={'pk': self.product.id}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_with_zero_rating(self):
        self.client.force_authenticate(user=self.user)
        data = {"rating": 0, "comment": "Not so good"}
        response = self.client.post(reverse('create-review', kwargs={'pk': self.product.id}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_without_comment(self):
        self.client.force_authenticate(user=self.user)
        data = {"rating": 4}
        response = self.client.post(reverse('create-review', kwargs={'pk': self.product.id}), data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
