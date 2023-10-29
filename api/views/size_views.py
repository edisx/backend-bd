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
def updateProductSizes(request):
    data = request.data
    product_id = data.get("product_id", None)
    size_ids = data.get("size_ids", [])  # This should be a list of size IDs

    if product_id is None or size_ids is None:
        return Response(
            {"detail": "product_id and size_ids are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Get sizes from IDs
    sizes_to_add = ShoeSize.objects.filter(id__in=size_ids)

    # Clear all sizes from the product first
    product.sizes.clear()

    # Add the sizes to the product
    product.sizes.add(*sizes_to_add)

    # Optionally, return the updated product
    serializer = ProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)
