from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import colorama

class UpdateUserProfileTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.update_url = reverse('user-profile-update')

        # Create token for the user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.update_data = {
            'name': 'Updated Name',
            'email': 'updated@example.com',
            'password': ''
        }

    def test_successful_profile_update(self):
        response = self.client.put(self.update_url, self.update_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, 'Updated Name')
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_update_without_password_change(self):
        self.update_data['password'] = ''
        response = self.client.put(self.update_url, self.update_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('testpassword'))

    def test_update_with_new_password(self):
        self.update_data['password'] = 'newpassword'
        response = self.client.put(self.update_url, self.update_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword'))

    def test_update_with_invalid_data(self):
        self.update_data['email'] = ''  # Removing email
        response = self.client.put(self.update_url, self.update_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access(self):
        self.client.credentials()  # Remove authentication
        response = self.client.put(self.update_url, self.update_data, format='json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

