from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.serializers import ShoeSizeSerializer, ProductSerializer
from api.models import ShoeSize, Product

from rest_framework import status



@api_view(["GET"])
def getSizes(request):
    sizes = ShoeSize.objects.all()
    serializer = ShoeSizeSerializer(sizes, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def addSize(request):
    data = request.data
    product_id = data.get('product_id', None)
    size_id = data.get('size_id', None)

    if not product_id or not size_id:
        return Response({"detail": "Both product_id and size_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        size = ShoeSize.objects.get(id=size_id)  # assuming ShoeSize is your size model
    except ShoeSize.DoesNotExist:
        return Response({"detail": "Size not found."}, status=status.HTTP_404_NOT_FOUND)

    product.sizes.add(size)  # assuming 'sizes' is the related name in your Product model for ShoeSize
    product.save()

    # Optionally, return the updated product
    serializer = ProductSerializer(product)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def removeSize(request):
    data = request.data
    product_id = data.get('product_id', None)
    size_id = data.get('size_id', None)

    if not product_id or not size_id:
        return Response({"detail": "Both product_id and size_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        size = ShoeSize.objects.get(id=size_id)
    except ShoeSize.DoesNotExist:
        return Response({"detail": "Size not found."}, status=status.HTTP_404_NOT_FOUND)

    if size in product.sizes.all():  # check if the size is associated with the product
        product.sizes.remove(size)
        product.save()
    else:
        return Response({"detail": "This size is not associated with the given product."}, status=status.HTTP_400_BAD_REQUEST)

    # Optionally, return the updated product
    serializer = ProductSerializer(product)

    return Response(serializer.data, status=status.HTTP_200_OK)

    
    