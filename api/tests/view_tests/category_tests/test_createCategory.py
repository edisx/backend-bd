from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Category
from django.contrib.auth.models import User
import colorama

class CreateCategoryTest(TestCase):
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

    def test_create_category_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('category-create'), {'name': 'New Category'})
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_create_category_without_name(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('category-create'), {})
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_duplicate_name(self):
        Category.objects.create(name='Existing Category')
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('category-create'), {'name': 'Existing Category'})
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Category with this name already exists')

    def test_create_category_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('category-create'), {'name': 'New Category'})
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
    
    

