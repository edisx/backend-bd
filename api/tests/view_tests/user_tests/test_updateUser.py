from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import colorama

class UpdateUserTest(APITestCase):

    def setUp(self):
        # Create a normal user
        self.user = User.objects.create_user(username='normaluser', email='normal@example.com', first_name='Normal', password='12345')
        # Create an admin user
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', first_name='Admin', password='admin12345')
        self.admin_token = self.get_tokens_for_user(self.admin_user)
        self.user_token = self.get_tokens_for_user(self.user)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_update_user_by_admin(self):
        self.api_authentication(self.admin_token)
        url = reverse('user-update', kwargs={'pk': self.user.id})
        data = {"name": "Updated Name", "email": "updated@example.com", "isAdmin": True}
        response = self.client.put(url, data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, "Updated Name")
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertTrue(self.user.is_staff)

    def test_update_user_by_non_admin(self):
        self.api_authentication(self.user_token)
        url = reverse('user-update', kwargs={'pk': self.admin_user.id})
        data = {"name": "New Name", "email": "newemail@example.com", "isAdmin": False}
        response = self.client.put(url, data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_unauthenticated(self):
        url = reverse('user-update', kwargs={'pk': self.user.id})
        data = {"name": "Another Name", "email": "anotheremail@example.com", "isAdmin": False}
        response = self.client.put(url, data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_non_existent_user(self):
        self.api_authentication(self.admin_token)
        url = reverse('user-update', kwargs={'pk': 9999})
        data = {"name": "Name", "email": "email@example.com", "isAdmin": False}
        response = self.client.put(url, data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

