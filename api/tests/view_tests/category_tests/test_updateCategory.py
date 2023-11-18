from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Category
from django.contrib.auth.models import User

class UpdateCategoryTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a test admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

        # Create a test non-admin user
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )

        # Create a category to be updated
        self.category = Category.objects.create(name="Original Category")

    def test_update_category_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(reverse('category-update', kwargs={'pk': self.category.pk}), {'name': 'Updated Category'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')

    def test_update_category_not_found(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(reverse('category-update', kwargs={'pk': 999}), {'name': 'Updated Category'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_category_without_name(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(reverse('category-update', kwargs={'pk': self.category.pk}), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_category_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('category-update', kwargs={'pk': self.category.pk}), {'name': 'Updated Category'})
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_update_nonexistent_category(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(reverse('category-update', kwargs={'pk': 999}), {'name': 'Updated Category'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    

