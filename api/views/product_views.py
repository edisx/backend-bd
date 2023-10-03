from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.serializers import ProductSerializer
from api.models import Product

@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)