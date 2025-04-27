from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LocationSerializer

class RegisterUser(APIView):
    """View for register a new user customer or driver"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'username': user.username,
                'is_driver': user.is_driver
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    """User authentication and JWT token generation."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Obtaining username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if both username and password are provided
        if not username or not password:
            return Response({"detail": "Username and password are mandatory."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user with the provided credentials
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # JWT token generation if the authentication is successful
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            })

        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

class LocationAssign(APIView):
    """Assigns a location to the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all locations for the authenticated user."""
        
        locations = LocationSerializer.get_user_location(request.user)

        if locations.exists():
            serializer = LocationSerializer(locations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No locations found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Assign a new location to the authenticated user."""
        data = request.data
        data['user'] = request.user.id

        serializer = LocationSerializer(data=data)

        if serializer.is_valid():
            location = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)