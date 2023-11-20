from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import ShoeSize
import colorama

class GetSizesTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        ShoeSize.objects.all().delete()
        ShoeSize.objects.create(size=40)
        ShoeSize.objects.create(size=41)
        ShoeSize.objects.create(size=42)

    def test_retrieve_sizes(self):
        response = self.client.get(reverse('sizes'))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sizes = response.json()
        self.assertEqual(len(sizes), 3)
        expected_sizes = [40, 41, 42]
        for size in sizes:
            self.assertIn(size['size'], expected_sizes)

    def test_retrieve_sizes_empty(self):
        ShoeSize.objects.all().delete()
        response = self.client.get(reverse('sizes'))
        print(colorama.Fore.MAGENTA + "Response Data:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sizes = response.json()
        self.assertEqual(len(sizes), 0)

