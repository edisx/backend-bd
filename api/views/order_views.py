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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrder(request):
    user = request.user
    data = request.data

    if not data:
        return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)

    orderItems = data.get('orderItems')

    if not orderItems or len(orderItems) == 0:
        return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)

    # (1) Create order
    order = Order.objects.create(
        user=user,
        payment_method=data['paymentMethod'],
        tax_price=data['taxPrice'],
        shipping_price=data['shippingPrice'],
        total_price=data['totalPrice']
    )

    # (2) Create shipping address
    shipping = ShippingAddress.objects.create(
        order=order,
        address=data['shippingAddress']['address'],
        city=data['shippingAddress']['city'],
        postal_code=data['shippingAddress']['postalCode'],
        country=data['shippingAddress']['country'],
    )

    # (3) Create order items and set order to orderItem relationship
    for i in orderItems:
        try:
            product = Product.objects.get(id=i['product'])
            size = ShoeSize.objects.get(id=i['size']['id']) if 'size' in i else None
        except ObjectDoesNotExist:
            return Response({'detail': 'Product does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        colors = i.get('colors', {})

        item = OrderItem.objects.create(
            product=product,
            order=order,
            name=i['name'],
            price=i['price'],
            image=i['image'],
            size=size,
            colors=colors
        )

    # (4) Update stock
    product.count_in_stock -= 1
    product.save()



    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user

    orders = user.order_set.all()

    serializer = OrderSerializer(orders, many=True)

    return Response(serializer.data)


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
            Response(
                {"detail": "Not authorized to view this order"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except:
        return Response(
            {"detail": "Order does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(id=pk)

    order.isPaid = True
    order.paidAt = datetime.now()

    order.save()

    return Response("Order was paid")


@api_view(["GET"])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all()

    serializer = OrderSerializer(orders, many=True)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    order = Order.objects.get(id=pk)

    order.isDelivered = True
    order.deliveredAt = timezone.now()

    order.save()

    return Response("Order was delivered")
