from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from api.serializers import UserSerializer, UserSerializerWithToken
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status

import logging

logger = logging.getLogger(__name__)



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["POST"])
def registerUser(request):
    """
    Register a new user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response containing the serialized user data.

    Raises:
        Response: If the required fields are missing or if a user with the same email already exists.
    """
    try:
        data = request.data

        # Basic validation for required fields
        if not data.get("email") or not data.get("password"):
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the user already exists
        if User.objects.filter(email=data["email"]).exists():
            return Response(
                {"error": "User with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create(
            first_name=data.get("name", ""),
            username=data["email"],
            email=data["email"],
            password=make_password(data["password"]),
        )

        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    """
    Update the user profile with the provided data.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object.

    Raises:
        Exception: If there is an internal server error.
    """
    try:
        user = request.user
        serializer = UserSerializerWithToken(user, many=False)

        data = request.data
        if not data.get('email'):
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        user.first_name = data["name"]
        user.username = data["email"]
        user.email = data["email"]

        if data["password"] != "":
            user.password = make_password(data["password"])

        user.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    """
    Retrieve the profile of the authenticated user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The serialized user profile data.

    Raises:
        Exception: If there is an internal server error.
    """
    try:
        user = request.user
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def getUsers(request):
    """
    Retrieve all users from the database and return a serialized response.

    Args:
        request: The HTTP request object.

    Returns:
        A Response object containing the serialized user data.

    Raises:
        Exception: If there is an internal server error.

    """
    try:
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def getUserById(request, pk):
    """
    Retrieve a user by their ID.

    Args:
        request: The HTTP request object.
        pk: The ID of the user to retrieve.

    Returns:
        A Response object containing the serialized user data if the user exists,
        or an error response if the user does not exist or an internal server error occurs.
    """
    try:
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(
            {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    """
    Delete a user by their ID.

    Args:
        request: The HTTP request object.
        pk: The ID of the user to be deleted.

    Returns:
        A Response object indicating the result of the deletion.

    Raises:
        User.DoesNotExist: If the user with the given ID does not exist.
        Exception: If an error occurs during user deletion.
    """
    try:
        userForDeletion = User.objects.get(id=pk)
        userForDeletion.delete()
        return Response("User was deleted")
    except User.DoesNotExist:
        return Response(
            {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "An error occurred during user deletion"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(["PUT"])
@permission_classes([IsAdminUser])
def updateUser(request, pk):
    try:
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)

        data = request.data
        user.first_name = data.get("name", user.first_name)
        user.username = data.get("email", user.username)
        user.email = data.get("email", user.email)
        user.is_staff = data.get("isAdmin", user.is_staff)

        user.save()

        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(
            {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "An error occurred during user update"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )