from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from api.models import Category
from api.serializers import CategorySerializer

class GetCategoriesTest(TestCase):
    def setUp(self):
        # Setup initial data
        Category.objects.create(name="Sneakers")
        Category.objects.create(name="Boots")
        Category.objects.create(name="Sandals")
        self.client = APIClient()

    def test_retrieve_categories(self):
        """
        Test retrieving all categories.
        """
        response = self.client.get(reverse('categories'))
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_no_categories(self):
        """
        Test retrieving categories when no categories exist.
        """
        Category.objects.all().delete()  # Clearing all category entries
        response = self.client.get(reverse('categories'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])  # Expecting an empty list

    