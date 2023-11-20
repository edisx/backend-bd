from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import colorama

class RegisterUserTestCase(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.user_data = {
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'password123'
        }

    def test_register_user_existing_email(self):
        User.objects.create_user(username='johndoe', email='johndoe@example.com', password='password123')
        response = self.client.post(self.register_url, self.user_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_register_user_invalid_data(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = ''  # Removing email
        response = self.client.post(self.register_url, invalid_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
