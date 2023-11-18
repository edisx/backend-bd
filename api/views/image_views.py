from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from api.serializers import ProductImageSerializer
from api.models import ProductImage, Product

from rest_framework import status


@api_view(["POST"])
@permission_classes([IsAdminUser])
def createImage(request):
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
        return Response(
            {"error": "Error occurred while adding the image"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def deleteImage(request, pk):
    try:
        imageForDeletion = ProductImage.objects.get(id=pk)
        imageForDeletion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ProductImage.DoesNotExist:
        return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An error occurred while deleting the image"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
