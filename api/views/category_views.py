from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.serializers import CategorySerializer
from api.models import Category

from rest_framework import status


@api_view(["GET"])
def getCategories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# category delete
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def deleteCategory(request, pk):
    categoryForDeletion = Category.objects.get(id=pk)
    categoryForDeletion.delete()
    return Response("Category deleted")


# category create
@api_view(["POST"])
@permission_classes([IsAdminUser])
def createCategory(request):
    if "name" not in request.data:
        return Response(
            {"error": "Name field is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    category = Category.objects.create(name=request.data["name"])
    serializer = CategorySerializer(category, many=False)
    return Response(serializer.data)


# category update
@api_view(["PUT"])
@permission_classes([IsAdminUser])
def updateCategory(request, pk):
    if "name" not in request.data:
        return Response(
            {"error": "Name field is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    category = Category.objects.get(id=pk)
    serializer = CategorySerializer(category, many=False)

    data = request.data
    category.name = data["name"]

    category.save()

    return Response(serializer.data)
