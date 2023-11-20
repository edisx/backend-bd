from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.serializers import ProductSerializer
from api.models import Product, Category, Review

from rest_framework import status

import logging

logger = logging.getLogger(__name__)




@api_view(["GET"])
def getProducts(request):
    """
    Retrieve all products.

    Args:
        request: The HTTP request object.

    Returns:
        A Response object containing the serialized data of all products.
        If an error occurs, a Response object with an error message and status code 500 is returned.
    """
    try:
        if request.user.is_staff:
            keyword = request.query_params.get('keyword', None)

            if keyword:
                products = Product.objects.filter(name__icontains=keyword)
            else:
                products = Product.objects.all()
        else:
            keyword = request.query_params.get('keyword', None)
            
            if keyword:
                products = Product.objects.filter(visible=True, name__icontains=keyword)
            else:
                products = Product.objects.filter(visible=True)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def getProduct(request, pk):
    """
    Retrieve a product by its ID.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the product to retrieve.

    Returns:
        Response: The HTTP response containing the serialized product data.

    Raises:
        Product.DoesNotExist: If the product with the given ID does not exist.
        Exception: If there is an internal server error.
    """
    try:
        if request.user.is_staff:
            product = Product.objects.get(id=pk)
        else:
            product = Product.objects.get(id=pk, visible=True)

        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not available."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# delete product
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    """
    Delete a product by its primary key.

    Args:
        request: The HTTP request object.
        pk: The primary key of the product to be deleted.

    Returns:
        A Response object with the appropriate status code.
        - If the product is successfully deleted, returns HTTP 204 No Content.
        - If the product does not exist, returns HTTP 404 Not Found.
        - If there is an internal server error, returns HTTP 500 Internal Server Error.
    """
    try:
        productForDeletion = Product.objects.get(id=pk)
        productForDeletion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# create product
@api_view(["POST"])
@permission_classes([IsAdminUser])
def createProduct(request):
    """
    Create a new product.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response containing the serialized product data.

    Raises:
        Exception: If there is an internal server error.

    """
    try:
        user = request.user
        product = Product.objects.create(
            user=user, name="product name", price=0, count_in_stock=0, description=""
        )
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(["PUT"])
@permission_classes([IsAdminUser])
def updateProduct(request, pk):
    """
    Update a product with the given ID.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the product to be updated.

    Returns:
        Response: The HTTP response containing the updated product data or an error message.

    Raises:
        Product.DoesNotExist: If the product with the given ID does not exist.
        Exception: If there is an internal server error.
    """
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, many=False)

        data = request.data
        product.name = data.get("name", product.name)
        product.price = data.get("price", product.price)
        product.description = data.get("description", product.description)
        product.count_in_stock = data.get("count_in_stock", product.count_in_stock)
        product.visible = data.get("visible", product.visible)

        category_id = data.get("category")

        if category_id == "":
            product.category = None
        elif category_id:
            try:
                category = Category.objects.get(id=category_id)
                product.category = category
            except Category.DoesNotExist:
                return Response({"error": "Category not found"}, status=404)

        product.save()

        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    """
    Create a new review for a product.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the product to be reviewed.

    Returns:
        Response: The HTTP response containing a success message or an error message.

    Raises:
        Product.DoesNotExist: If the product with the given ID does not exist.
        Exception: If there is an internal server error.
    """
    try:
        user = request.user
        product = Product.objects.get(id=pk)
        data = request.data

        # 1 - Review already exists
        alreadyExists = product.reviews.filter(user=user).exists()
        if alreadyExists:
            content = {"error": "Product already reviewed"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # 2 - No Rating or 0
        rating = int(data.get("rating", 0))  # Convert rating to an integer
        if rating == 0:
            content = {"error": "Please select a valid rating"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # 2.5 - No Comment
        comment = data.get("comment", "").strip()
        if comment == "":
            content = {"error": "Please enter a comment"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # 3 - Create review
        review = Review.objects.create(
            user=user,
            product=product,
            name=user.first_name,
            rating=rating,
            comment=comment,
        )

        reviews = product.reviews.all()
        product.num_reviews = len(reviews)

        total = sum(i.rating for i in reviews)
        product.rating = total / len(reviews) if reviews else 0
        product.save()
        
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteProductReview(request, pk, review_id):
    """
    Delete a product review.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the product.
        review_id (int): The ID of the review to be deleted.

    Returns:
        Response: The HTTP response object.
    """
    try:
        user = request.user
        product = Product.objects.get(id=pk)
        review = Review.objects.get(id=review_id)

        if not user.is_staff and review.user != user:
            content = {"error": "You are not authorized to delete this review"}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)
        else:
            review.delete()
            reviews = product.reviews.all()
            product.num_reviews = len(reviews)

            total = 0
            for i in reviews:
                total += i.rating
            
            if len(reviews) > 0:
                product.rating = total / len(reviews)
            else:
                product.rating = 0
            
            product.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Review.DoesNotExist:
        return Response(
            {"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    
    





