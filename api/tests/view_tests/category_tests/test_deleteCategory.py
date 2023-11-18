from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Category
from django.contrib.auth.models import User

class DeleteCategoryTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a test admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

        # Create some categories
        self.category1 = Category.objects.create(name="Sneakers")
        self.category2 = Category.objects.create(name="Boots")

    def test_delete_category_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('category-delete', kwargs={'pk': self.category1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check if the category is actually deleted
        self.assertFalse(Category.objects.filter(pk=self.category1.pk).exists())

    def test_category_not_found(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('category-delete', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Category not found')

    def test_delete_category_unauthorized(self):
        # Create a non-admin user and try to delete a category
        non_admin_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )
        self.client.force_authenticate(user=non_admin_user)
        response = self.client.delete(reverse('category-delete', kwargs={'pk': self.category2.pk}))
        self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT)