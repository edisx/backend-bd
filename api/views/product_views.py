from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.serializers import ProductSerializer
from api.models import Product, Category

from rest_framework import status


@api_view(["GET"])
def getProducts(request):
    if request.user.is_staff:
        products = Product.objects.all()
    else:
        products = Product.objects.filter(visible=True)

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getProduct(request, pk):
    try:
        if request.user.is_staff:
            product = Product.objects.get(id=pk)
        else:
            product = Product.objects.get(id=pk, visible=True)

        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(
            {"detail": "Product not available."}, status=status.HTTP_404_NOT_FOUND
        )


# delete product
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    productForDeletion = Product.objects.get(id=pk)
    productForDeletion.delete()
    return Response("Product deleted")


# create product
@api_view(["POST"])
@permission_classes([IsAdminUser])
def createProduct(request):
    user = request.user
    product = Product.objects.create(
        user=user, name="product name", price=0, count_in_stock=0, description=""
    )
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAdminUser])
def updateProduct(request, pk):
    product = Product.objects.get(id=pk)
    serializer = ProductSerializer(product, many=False)

    data = request.data
    product.name = data.get("name", product.name)
    product.price = data.get("price", product.price)
    product.description = data.get("description", product.description)
    product.count_in_stock = data.get("count_in_stock", product.count_in_stock)

    category_id = data.get("category")

    if category_id == "":
        product.category = None
    elif category_id:
        try:
            category = Category.objects.get(id=category_id)
            product.category = category
        except Category.DoesNotExist:
            return Response({"detail": "Category not found"}, status=404)

    product.save()

    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


# upload images


# upload 3d model
