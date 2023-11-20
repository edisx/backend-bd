from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from api.models import Product, Order, OrderItem, ShippingAddress, ShoeSize
from api.serializers import ProductSerializer, OrderSerializer
from rest_framework import status
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import JsonResponse

import logging

logger = logging.getLogger(__name__)



# get all orders
@api_view(["GET"])
@permission_classes([IsAdminUser])
def getOrders(request):
    """
    Retrieve all orders.

    Args:
        request: The HTTP request object.

    Returns:
        A Response object containing the serialized data of all orders.
        If an exception occurs, a Response object with an error message and
        a status code of 500 will be returned.
    """
    try:
        orders = Order.objects.all()

        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# get order by id
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    """
    Retrieve an order by its ID.

    Args:
        request (Request): The request object.
        pk (int): The ID of the order to retrieve.

    Returns:
        Response: The response containing the serialized order data.

    Raises:
        Order.DoesNotExist: If the order with the given ID does not exist.
        Exception: If there is an internal server error.
    """
    try:
        user = request.user
        order = Order.objects.get(id=pk)

        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Not authorized to view this order"},
                status=status.HTTP_403_FORBIDDEN,
            )
    except Order.DoesNotExist:
        return Response(
            {"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addOrder(request):
    """
    Add an order to the system.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object containing the serialized order data.

    Raises:
        JsonResponse: If there are no order items, or if there is insufficient stock for a product,
            or if a product with a given ID does not exist.
    """
    try:
        user = request.user
        data = request.data

        if not data or not data.get("orderItems"):
            return Response(
                {"error": "No Order Items"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Step 1: Aggregate Product Quantities
            product_quantities = {}
            for item_data in data["orderItems"]:
                product_id = item_data["product"]
                product_quantities[product_id] = product_quantities.get(product_id, 0) + 1

            # Step 2: Check Stock Availability
            for product_id, quantity in product_quantities.items():
                try:
                    product = Product.objects.get(id=product_id)
                    if quantity > product.count_in_stock:
                        return JsonResponse(
                            {"error": f"Insufficient stock for product '{product.name}'"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                except Product.DoesNotExist:
                    return JsonResponse(
                        {"error": f"Product with ID {product_id} does not exist"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Create order
            order = Order.objects.create(
                user=user,
                payment_method=data["paymentMethod"],
                tax_price=data["taxPrice"],
                shipping_price=data["shippingPrice"],
                total_price=data["totalPrice"],
            )

            # Create shipping address
            shipping = ShippingAddress.objects.create(
                order=order,
                address=data["shippingAddress"]["address"],
                city=data["shippingAddress"]["city"],
                postal_code=data["shippingAddress"]["postalCode"],
                country=data["shippingAddress"]["country"],
            )

            # Create order items
            for item_data in data["orderItems"]:
                product = Product.objects.get(id=item_data["product"])
                size = (
                    ShoeSize.objects.get(id=item_data["size"]["id"])
                    if "size" in item_data
                    else None
                )
                colors = item_data.get("colors", {})

                OrderItem.objects.create(
                    product=product,
                    order=order,
                    name=item_data["name"],
                    price=item_data["price"],
                    image=item_data["image"],
                    size=size,
                    colors=colors,
                )

            # Step 3: Update Stock
            for product_id, quantity in product_quantities.items():
                product = Product.objects.get(id=product_id)
                product.count_in_stock -= quantity
                product.save()

        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# get my orders
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    """
    Retrieve all orders associated with the authenticated user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object containing the serialized order data.

    Raises:
        Exception: If there is an internal server error.

    """
    try:
        user = request.user

        orders = user.orders.all()

        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# update order to paid
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    """
    Update the order status to paid.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the order.

    Returns:
        Response: The HTTP response containing the serialized order data if successful,
        or an error response if the order does not exist or an internal server error occurs.
    """
    try:
        order = Order.objects.get(id=pk)

        if not request.user.is_staff and order.user != request.user:
            return Response({"error": "Not authorized to update this order"}, status=status.HTTP_403_FORBIDDEN)

        order.is_paid = True
        order.paid_at = timezone.now()

        order.save()
        serializer = OrderSerializer(order, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )





# update order to delivered
@api_view(["PUT"])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    """
    Update the order status to delivered.

    Args:
        request: The HTTP request object.
        pk: The primary key of the order to be updated.

    Returns:
        A Response object with the serialized data of the updated order or an error message.

    Raises:
        ObjectDoesNotExist: If the order with the given primary key does not exist.
        Exception: If there is an internal server error.
    """
    try:
        order = Order.objects.get(id=pk)

        order.is_delivered = True
        order.delivered_at = timezone.now()

        order.save()
        serializer = OrderSerializer(order, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
