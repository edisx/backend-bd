from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import colorama

class GetUserByIdTest(APITestCase):

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

    def test_get_user_by_id_admin(self):
        self.api_authentication(self.admin_token)
        url = reverse('user', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_get_user_by_id_non_admin(self):
        self.api_authentication(self.user_token)
        url = reverse('user', kwargs={'pk': self.admin_user.id})
        response = self.client.get(url)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_by_id_unauthenticated(self):
        url = reverse('user', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_by_id_not_found(self):
        self.api_authentication(self.admin_token)
        url = reverse('user', kwargs={'pk': 9999}) 
        response = self.client.get(url)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

