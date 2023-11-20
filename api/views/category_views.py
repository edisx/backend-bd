from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from api.serializers import CategorySerializer
from api.models import Category

from rest_framework import status

import logging

logger = logging.getLogger(__name__)


@api_view(["GET"])
def getCategories(request):
    """
    Retrieve all categories from the database and return them as a response.

    Args:
        request: The HTTP request object.

    Returns:
        A Response object containing the serialized data of all categories.
        If an exception occurs, a Response object with an error message and
        status code 500 will be returned.
    """
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def deleteCategory(request, pk):
    """
    Delete a category by its primary key.

    Args:
        request: The HTTP request object.
        pk (int): The primary key of the category to be deleted.

    Returns:
        Response: The HTTP response indicating the result of the deletion.
            - If the category is successfully deleted, returns HTTP 204 No Content.
            - If the category does not exist, returns HTTP 404 Not Found.
            - If an error occurs during the deletion process, returns HTTP 500 Internal Server Error.
    """
    try:
        categoryForDeletion = Category.objects.get(id=pk)
        categoryForDeletion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response(
            {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "An error occurred during category deletion"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def createCategory(request):
    """
    Create a new category.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object containing the created category data.

    Raises:
        Exception: If an error occurs during category creation.
    """
    try:
        if "name" not in request.data:
            return Response(
                {"error": "Name field is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if Category.objects.filter(name=request.data["name"]).exists():
            return Response(
                {"error": "Category with this name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = Category.objects.create(name=request.data["name"])
        serializer = CategorySerializer(category, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "An error occurred during category creation"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAdminUser])
def updateCategory(request, pk):
    """
    Update a category with the given primary key.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the category to be updated.

    Returns:
        Response: The HTTP response object containing the updated category data or an error message.

    Raises:
        Category.DoesNotExist: If the category with the given primary key does not exist.
        Exception: If an error occurs during category update.
    """
    try:
        category = Category.objects.get(id=pk)
        serializer = CategorySerializer(category, data=request.data, many=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Category.DoesNotExist:
        return Response(
            {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "An error occurred during category update"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
