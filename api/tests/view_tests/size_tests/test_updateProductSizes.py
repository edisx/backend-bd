from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from api.models import Product, ShoeSize
from rest_framework_simplejwt.tokens import RefreshToken
import json
import colorama

class UpdateProductSizesTest(APITestCase):

    def setUp(self):
        # Clear existing ShoeSize entries
        ShoeSize.objects.all().delete()
        # Create a normal user
        self.user = User.objects.create_user(username='normaluser', password='12345')
        # Create an admin user
        self.admin_user = User.objects.create_superuser(username='adminuser', password='admin12345')
        self.admin_token = self.get_tokens_for_user(self.admin_user)
        # Create sample product
        self.product = Product.objects.create(name="Sample Product", price=9.99, user=self.admin_user)
        # Create sample shoe sizes
        self.shoe_sizes = [ShoeSize.objects.create(size=i) for i in range(1, 6)]

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_update_product_sizes_success(self):
        self.api_authentication(self.admin_token)
        url = reverse('sizes-update')

        shoe_size_ids = [12, 13, 14, 15, 16]
        data = {"product_id": self.product.id, "size_ids": shoe_size_ids}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(set(self.product.sizes.values_list('id', flat=True)), set(shoe_size_ids))


    def test_update_product_sizes_non_admin(self):
        self.api_authentication(self.get_tokens_for_user(self.user))
        url = reverse('sizes-update')
        data = {"product_id": self.product.id, "size_ids": [1, 2]}
        response = self.client.post(url, data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_sizes_unauthenticated(self):
        # Test update attempt without authentication
        url = reverse('sizes-update')
        data = {"product_id": self.product.id, "size_ids": [1, 2]}
        response = self.client.post(url, data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_sizes_invalid_data(self):
        self.api_authentication(self.admin_token)
        url = reverse('sizes-update')
        data = {"product_id": 9999, "size_ids": [99, 100]} 
        response = self.client.post(url, data)
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

