from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from api.serializers import ProductImageSerializer
from api.models import ProductImage, Product

from rest_framework import status
from api.permissions import IsSuperUser

import os
from django.conf import settings
from django.core.files.storage import default_storage

import logging

logger = logging.getLogger(__name__)



@api_view(["POST"])
@permission_classes([IsSuperUser])
def createImage(request):
    """
    Create a new image for a product.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object containing the serialized image data.

    Raises:
        Product.DoesNotExist: If the specified product does not exist.
        Exception: If an error occurs while adding the image.
    """
    try:
        data = request.data
        product_id = data["product_id"]
        product = Product.objects.get(id=product_id)

        image = ProductImage(product=product, image=data["image"])
        image.save()

        serializer = ProductImageSerializer(image, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Product.DoesNotExist:
        return Response(
            {"error": "Product does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Error occurred while adding the image"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsSuperUser])
def deleteImage(request, pk):
    """
    Delete an image by its primary key.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the image to be deleted.

    Returns:
        Response: The HTTP response indicating the result of the deletion.
            - If the image is successfully deleted, returns HTTP 204 No Content.
            - If the image is not found, returns HTTP 404 Not Found with an error message.
            - If an error occurs during the deletion process, returns HTTP 500 Internal Server Error with an error message.
    """
    try:
        image_for_deletion = ProductImage.objects.get(id=pk)

        # Delete the image from the associated product
        product = image_for_deletion.product
        if product and product.model_3d:
            if settings.USE_LOCAL:
                # Local storage logic
                image_file_path = os.path.join(settings.MEDIA_ROOT, image_for_deletion.image.name)
                if os.path.exists(image_file_path):
                    os.remove(image_file_path)
            else:
                # S3
                default_storage.delete(image_for_deletion.image.name)

        image_for_deletion.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    except ProductImage.DoesNotExist:
        return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "An error occurred while deleting the image"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
