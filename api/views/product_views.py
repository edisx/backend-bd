from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.serializers import ProductSerializer
from api.models import Product, Category, Review

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
    return Response(status=status.HTTP_204_NO_CONTENT)


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
    product.visible = data.get("visible", product.visible)

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



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    user = request.user
    product = Product.objects.get(id=pk)
    data = request.data

    # 1 - Review already exists
    alreadyExists = product.reviews.filter(user=user).exists()

    if alreadyExists:
        content = {"message": "Product already reviewed"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    

    # 2 - No Rating or 0
    elif "rating" not in data or data["rating"] == 0:
        content = {"message": "Please select a valid rating"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # 2.5 - No Comment
    elif "comment" not in data or data["comment"].strip() == "":
        content = {"message": "Please enter a comment"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # 3 - Create review
    else:
        review = Review.objects.create(
            user=user,
            product=product,
            name=user.first_name,
            rating=data["rating"],
            comment=data["comment"],
        )

        reviews = product.reviews.all()
        product.num_reviews = len(reviews)

        total = 0
        for i in reviews:
            total += i.rating
        
        product.rating = total / len(reviews)
        product.save()
        
        return Response("Review added")
    

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteProductReview(request, pk, review_id):
    user = request.user
    product = Product.objects.get(id=pk)
    review = Review.objects.get(id=review_id)

    if not user.is_staff and review.user != user:
        content = {"detail": "You are not authorized to delete this review"}
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

    
    





