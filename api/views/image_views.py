from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from api.serializers import ProductImageSerializer
from api.models import ProductImage, Product

from rest_framework import status



# add image to product
@api_view(["POST"])
@permission_classes([IsAdminUser])
def createImage(request):
    data = request.data

    try:
        # Get the product to which the image will be attached
        product_id = data['product_id']
        product = Product.objects.get(id=product_id)

        # Create a new image for the product
        image = ProductImage(product=product, image=data['image'])
        image.save()

        # Serialize the created image and return it in the response
        serializer = ProductImageSerializer(image, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Product.DoesNotExist:
        message = {'detail': 'Product does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        message = {'detail': 'Error occurred while adding the image'}
        return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# delete image
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def deleteImage(request, pk):
    try:
        imageForDeletion = ProductImage.objects.get(id=pk)
        imageForDeletion.delete()
        return Response("Image deleted", status=status.HTTP_200_OK)
    except ProductImage.DoesNotExist:
        return Response({"detail": "Image not found"}, status=status.HTTP_404_NOT_FOUND)


