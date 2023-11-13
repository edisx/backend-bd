from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from api.models import Product, Order, OrderItem, ShippingAddress, ShoeSize
from api.serializers import ProductSerializer, OrderSerializer
from rest_framework import status
from datetime import datetime
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import JsonResponse


# get all orders
@api_view(["GET"])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all()

    serializer = OrderSerializer(orders, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addOrder(request):
    user = request.user
    data = request.data

    if not data or not data.get("orderItems"):
        return Response({"detail": "No Order Items"}, status=status.HTTP_400_BAD_REQUEST)

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
                    return JsonResponse({"detail": f"Insufficient stock for product '{product.name}'"},
                                        status=status.HTTP_400_BAD_REQUEST)
            except Product.DoesNotExist:
                return JsonResponse({"detail": f"Product with ID {product_id} does not exist"},
                                    status=status.HTTP_400_BAD_REQUEST)

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
            size = ShoeSize.objects.get(id=item_data["size"]["id"]) if "size" in item_data else None
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
    return Response(serializer.data)


# get order by id
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    user = request.user

    try:
        order = Order.objects.get(id=pk)

        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "Not authorized to view this order"},
                status=status.HTTP_403_FORBIDDEN,
            )
    except Order.DoesNotExist:
        return Response(
            {"detail": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND
        )


# update order to paid
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(id=pk)

    order.is_paid = True
    order.paid_at = datetime.now()

    order.save()

    return Response("Order was paid")

# get my orders
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user

    orders = user.orders.all()

    serializer = OrderSerializer(orders, many=True)

    return Response(serializer.data)





# update order to delivered
@api_view(["PUT"])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    order = Order.objects.get(id=pk)

    order.is_delivered = True
    order.delivered_at = timezone.now()

    order.save()

    return Response("Order was delivered")
