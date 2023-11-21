from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.serializers import ShoeSizeSerializer, ProductSerializer
from api.models import ShoeSize, Product, ActionLog

from rest_framework import status

import logging

logger = logging.getLogger(__name__)



@api_view(["GET"])
def getSizes(request):
    """
    Retrieve all shoe sizes and return them as a response.

    Args:
        request: The HTTP request object.

    Returns:
        A Response object containing the serialized shoe sizes data.

    Raises:
        Exception: If there is an internal server error.
    """
    try:
        sizes = ShoeSize.objects.all()
        serializer = ShoeSizeSerializer(sizes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def updateProductSizes(request):
    try:
        data = request.data
        product_id = data.get("product_id")
        size_ids = data.get("size_ids")


        if product_id is None or size_ids is None:
            return Response(
                {"error": "product_id and size_ids are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(size_ids, list):
            return Response(
                {"error": "size_ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        current_size_ids = set(product.sizes.values_list('id', flat=True))
        new_size_ids = set(size_ids)

        current_sizes = ShoeSize.objects.filter(id__in=current_size_ids).values_list('size', flat=True)
        new_sizes = ShoeSize.objects.filter(id__in=new_size_ids).values_list('size', flat=True)


        if current_size_ids == new_size_ids:
            return Response(
                {"detail": "Product sizes are already up to date."},
                status=status.HTTP_200_OK
            )
        
        

        valid_sizes = ShoeSize.objects.filter(id__in=size_ids)
        if not valid_sizes.exists():
            return Response(
                {"error": "One or more size_ids are invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product.sizes.clear()
        product.sizes.add(*valid_sizes)

        # Format the sizes for logging
        formatted_current_sizes = ', '.join(map(str, current_sizes))
        formatted_new_sizes = ', '.join(map(str, new_sizes))

        ActionLog.objects.create(
            user=request.user,
            action=f"User {request.user.first_name} updated product sizes for {product.name} from [{formatted_current_sizes}] to [{formatted_new_sizes}]."
        )



        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )