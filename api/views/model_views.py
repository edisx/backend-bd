from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from api.models import Product, Color, Mesh

from rest_framework import status

import os
from django.conf import settings

from api.serializers import ProductSerializer, MeshSerializer, ColorSerializer
from django.core.files.uploadedfile import UploadedFile
from api.permissions import IsSuperUser

import logging

logger = logging.getLogger(__name__)



@api_view(['POST'])
@permission_classes([IsSuperUser])
def createModel(request):
    """
    TODO: tests
    Create a new model for a product.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object containing the created model data or an error message.

    Raises:
        Product.DoesNotExist: If the specified product ID does not exist.
        Exception: If an error occurs while adding the model.
    """
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
            return Response({"error": "No 3D model file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate if the file is a .glb file
        if isinstance(model_3d_file, UploadedFile) and not model_3d_file.name.endswith('.glb'):
            return Response({"error": "Model must be a .glb file"}, status=status.HTTP_400_BAD_REQUEST)

        # Set the model_3d field to the uploaded file and save
        product.model_3d = model_3d_file
        product.save()
        serializer = ProductSerializer(product, many=False)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(e)
        return Response({"error": "Error occurred while adding the model"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsSuperUser])
def deleteModel(request, pk):
    """
    TODO: tests
    Delete the 3D model and associated meshes of a product.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the product.

    Returns:
        Response: The HTTP response object.
            - If the model and meshes are successfully deleted, returns a success message with status 200 (OK).
            - If the product is not found, returns an error message with status 404 (Not Found).
            - If an error occurs during deletion, returns an error message with status 500 (Internal Server Error).
    """
    try:
        product = Product.objects.get(id=pk)

        # Delete all the meshes associated with the product
        Mesh.objects.filter(product=product).delete()

        # Delete the 3D model file if it exists
        if product.model_3d:
            file_path = os.path.join(settings.MEDIA_ROOT, product.model_3d.path)
            if os.path.exists(file_path):
                os.remove(file_path)

        product.model_3d = None
        product.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(e)
        return Response({"error": "An error occurred while deleting the model"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# add color to mesh
@api_view(['POST'])
@permission_classes([IsSuperUser])
def addColor(request):
    """
    TODO: tests
    Add a new color for a mesh.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: The HTTP response object.

    Raises:
        Exception: If an error occurs while adding the color.
    """
    try:
        data = request.data

        # Ensure mesh_id is present in the data
        mesh_id = data.get('mesh_id')
        if not mesh_id:
            return Response({"error": "No mesh ID provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the mesh exists
        try:
            mesh = Mesh.objects.get(id=mesh_id)
        except Mesh.DoesNotExist:
            return Response({"error": "Mesh not found."}, status=status.HTTP_404_NOT_FOUND)

        # Extract color details
        color_name = data.get('color_name')
        hex_code = data.get('hex_code')

        # Validate color details
        if not color_name or not hex_code:
            return Response({"error": "Color name or hex code not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the color for the mesh already exists
        if Color.objects.filter(mesh=mesh, color_name=color_name).exists():
            return Response({"error": "Color already exists for this mesh."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the new color
        color = Color(mesh=mesh, color_name=color_name, hex_code=hex_code)
        color.save()

        serializer = ColorSerializer(color, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(e)
        return Response({"error": "An error occurred while adding the color"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# update color
@api_view(['PUT'])
@permission_classes([IsSuperUser])
def updateColor(request, pk):
    """
    TODO: tests
    Update the details of a color.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the color to be updated.

    Returns:
        Response: The HTTP response containing the updated color details.

    Raises:
        Color.DoesNotExist: If the color with the given ID does not exist.
        Exception: If an error occurs while updating the color.
    """
    try:
        data = request.data

        # Ensure pk is present in the data
        if not pk:
            return Response({"error": "No color ID provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the color exists
        try:
            color = Color.objects.get(id=pk)
        except Color.DoesNotExist:
            return Response({"error": "Color not found."}, status=status.HTTP_404_NOT_FOUND)

        # Extract color details
        color_name = data.get('color_name')
        hex_code = data.get('hex_code')

        # Validate color details
        if not color_name or not hex_code:
            return Response({"error": "Color name or hex code not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the color
        color.color_name = color_name
        color.hex_code = hex_code
        color.save()

        serializer = ColorSerializer(color, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(e)
        return Response({"error": "An error occurred while updating the color"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# remove color from mesh
@api_view(['DELETE'])
@permission_classes([IsSuperUser])
def deleteColor(request, pk):
    """
    TODO: tests
    Delete a color object.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the color object to be deleted.

    Returns:
        Response: HTTP response indicating the success or failure of the deletion.
    """
    try:
        # Ensure pk is present in the data
        if not pk:
            return Response({"error": "No color ID provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the color exists
        try:
            color = Color.objects.get(id=pk)
        except Color.DoesNotExist:
            return Response({"error": "Color not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the color
        color.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(e)
        return Response({"error": "An error occurred while deleting the color"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
@permission_classes([IsSuperUser])
def addColors(request):
    """
    TODO: tests
    Not featured in actual website, but used for testing purposes.
    """
    data = request.data

    # Ensure mesh_id is present in the data
    mesh_id = data.get('mesh_id')
    if not mesh_id:
        return Response({"error": "No mesh ID provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the mesh exists
    try:
        mesh = Mesh.objects.get(id=mesh_id)
    except Mesh.DoesNotExist:
        return Response({"error": "Mesh not found."}, status=status.HTTP_404_NOT_FOUND)

    # Expecting 'colors' to be a list of color data
    colors_data = data.get('colors')
    if not colors_data or not isinstance(colors_data, list):
        return Response({"error": "Invalid or missing colors data."}, status=status.HTTP_400_BAD_REQUEST)

    for color_data in colors_data:
        color_name = color_data.get('color_name')
        hex_code = color_data.get('hex_code')

        # Validate each color's details
        if not color_name or not hex_code:
            return Response({"error": "Color name or hex code not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the color for the mesh already exists
        if Color.objects.filter(mesh=mesh, color_name=color_name).exists():
            continue  # Skip adding this color if it already exists

        # Create the new color
        color = Color(mesh=mesh, color_name=color_name, hex_code=hex_code)
        color.save()
    
    serializer = ColorSerializer(mesh.colors, many=True)

    return Response(serializer.data, status=status.HTTP_201_CREATED)



