from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from api.models import Product, Color, Mesh

from rest_framework import status

import os
from django.conf import settings

from api.serializers import ProductSerializer, MeshSerializer, ColorSerializer




# add new model to product
@api_view(['POST'])
@permission_classes([IsAdminUser])
def createModel(request):
    try:
        data = request.data
        product_id = data.get('product_id')
        if not product_id:
            return Response({"error": "No product ID provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the uploaded 3D model file from the request
        model_3d_file = request.FILES.get('model_3d')
        if not model_3d_file:
            return Response({"errpr": "No 3D model file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Set the model_3d field to the uploaded file and save
        product.model_3d = model_3d_file
        product.save()
        serializer = ProductSerializer(product, many=False)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": "Error occurred while adding the model"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteModel(request, pk):
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    # Delete all the meshes associated with the product
    Mesh.objects.filter(product=product).delete()

    # Delete the 3D model file if it exists
    if product.model_3d:
        file_path = os.path.join(settings.MEDIA_ROOT, product.model_3d.path)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Set the model_3d field to None and save
    product.model_3d = None
    product.save()

    return Response({"detail": "Model and associated meshes deleted successfully."}, status=status.HTTP_200_OK)



# add color to mesh
@api_view(['POST'])
@permission_classes([IsAdminUser])
def addColor(request):
    data = request.data

    # Ensure mesh_id is present in the data
    mesh_id = data.get('mesh_id')
    if not mesh_id:
        return Response({"detail": "No mesh ID provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the mesh exists
    try:
        mesh = Mesh.objects.get(id=mesh_id)
    except Mesh.DoesNotExist:
        return Response({"detail": "Mesh not found."}, status=status.HTTP_404_NOT_FOUND)

    # Extract color details
    color_name = data.get('color_name')
    hex_code = data.get('hex_code')

    # Validate color details
    if not color_name or not hex_code:
        return Response({"detail": "Color name or hex code not provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the color for the mesh already exists
    if Color.objects.filter(mesh=mesh, color_name=color_name).exists():
        return Response({"detail": "Color already exists for this mesh."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the new color
    color = Color(mesh=mesh, color_name=color_name, hex_code=hex_code)
    color.save()

    return Response({"detail": "Color added successfully."}, status=status.HTTP_201_CREATED)


# update color
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateColor(request, pk):
    data = request.data

    # Ensure pk is present in the data
    if not pk:
        return Response({"detail": "No color ID provided."}, status=status.HTTP_400_BAD_REQUEST)


    # Check if the color exists
    try:
        color = Color.objects.get(id=pk)
    except Color.DoesNotExist:
        return Response({"detail": "Color not found."}, status=status.HTTP_404_NOT_FOUND)

    # Extract color details
    color_name = data.get('color_name')
    hex_code = data.get('hex_code')

    # Validate color details
    if not color_name or not hex_code:
        return Response({"detail": "Color name or hex code not provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Update the color
    color.color_name = color_name
    color.hex_code = hex_code
    color.save()

    return Response({"detail": "Color updated successfully."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def addColors(request):
    data = request.data

    # Ensure mesh_id is present in the data
    mesh_id = data.get('mesh_id')
    if not mesh_id:
        return Response({"detail": "No mesh ID provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the mesh exists
    try:
        mesh = Mesh.objects.get(id=mesh_id)
    except Mesh.DoesNotExist:
        return Response({"detail": "Mesh not found."}, status=status.HTTP_404_NOT_FOUND)

    # Expecting 'colors' to be a list of color data
    colors_data = data.get('colors')
    if not colors_data or not isinstance(colors_data, list):
        return Response({"detail": "Invalid or missing colors data."}, status=status.HTTP_400_BAD_REQUEST)

    for color_data in colors_data:
        color_name = color_data.get('color_name')
        hex_code = color_data.get('hex_code')

        # Validate each color's details
        if not color_name or not hex_code:
            return Response({"detail": "Color name or hex code not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the color for the mesh already exists
        if Color.objects.filter(mesh=mesh, color_name=color_name).exists():
            continue  # Skip adding this color if it already exists

        # Create the new color
        color = Color(mesh=mesh, color_name=color_name, hex_code=hex_code)
        color.save()

    return Response({"detail": "Colors added successfully."}, status=status.HTTP_201_CREATED)


# remove color from mesh
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteColor(request, pk):
    # Ensure pk is present in the data
    if not pk:
        return Response({"detail": "No color ID provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the color exists
    try:
        color = Color.objects.get(id=pk)
    except Color.DoesNotExist:
        return Response({"detail": "Color not found."}, status=status.HTTP_404_NOT_FOUND)

    # Delete the color
    color.delete()

    return Response({"detail": "Color deleted successfully."}, status=status.HTTP_200_OK)





