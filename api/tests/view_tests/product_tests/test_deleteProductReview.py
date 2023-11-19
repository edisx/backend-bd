from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Product, Review
import colorama

class DeleteProductReviewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('user', 'user@example.com', 'password123')
        self.another_user = User.objects.create_user('another_user', 'another_user@example.com', 'password123')
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password123')
        self.product = Product.objects.create(name="Test Product", price=30.00, count_in_stock=10)
        self.review = Review.objects.create(user=self.user, product=self.product, rating=4, comment="Good product")

    def test_delete_review_by_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('delete-review', kwargs={'pk': self.product.id, 'review_id': self.review.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_by_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('delete-review', kwargs={'pk': self.product.id, 'review_id': self.review.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthorized_review_deletion(self):
        self.client.force_authenticate(user=self.another_user)
        response = self.client.delete(reverse('delete-review', kwargs={'pk': self.product.id, 'review_id': self.review.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_nonexistent_review(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('delete-review', kwargs={'pk': self.product.id, 'review_id': 999}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review_nonexistent_product(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('delete-review', kwargs={'pk': 999, 'review_id': self.review.id}))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
