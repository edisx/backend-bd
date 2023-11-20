from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import colorama

class DeleteUserTest(APITestCase):

    def setUp(self):
        # Create a normal user
        self.user = User.objects.create_user(username='normaluser', password='12345')
        # Create an admin user
        self.admin_user = User.objects.create_superuser(username='adminuser', password='admin12345')
        self.admin_token = self.get_tokens_for_user(self.admin_user)
        self.user_token = self.get_tokens_for_user(self.user)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_delete_user_by_admin(self):
        self.api_authentication(self.admin_token)
        url = reverse('user-delete', kwargs={'pk': self.user.id})
        response = self.client.delete(url)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_user_by_non_admin(self):
        self.api_authentication(self.user_token)
        url = reverse('user-delete', kwargs={'pk': self.admin_user.id})
        response = self.client.delete(url)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_unauthenticated(self):
        url = reverse('user-delete', kwargs={'pk': self.user.id})
        response = self.client.delete(url)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_non_existent_user(self):
        self.api_authentication(self.admin_token)
        url = reverse('user-delete', kwargs={'pk': 9999})
        response = self.client.delete(url)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

