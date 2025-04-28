from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LocationSerializer, ServiceRequestSerializer
from .utils import nearest_driver, estimated_time, get_latest_user_location
from .models import ServiceRequest
import json

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

class ServiceRequestCreate(APIView):
    """Allows only non-driver users to create a service request, assigning the nearest driver."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new service request if user is not a driver."""

        user = request.user

        if user.is_driver:
            return Response({"detail": "Drivers cannot create service requests."},
                            status=status.HTTP_403_FORBIDDEN)

         # Get latest user location
        latest_location = get_latest_user_location(user)

        if not latest_location:
            return Response({"detail": "You must have at least one location registered."},
                            status=status.HTTP_400_BAD_REQUEST)

        pickup_latitude = latest_location.latitude
        pickup_longitude = latest_location.longitude

        # Check if there's already an uncompleted service request with this customer and driver
        existing_request = ServiceRequest.objects.filter(
            customer=user, driver__isnull=False, is_completed=False
        ).first()

        if existing_request:
            return Response({
                "detail": "You already have an uncompleted service request with a driver."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find nearest driver
        driver = nearest_driver(pickup_latitude, pickup_longitude)

        if driver is None:
            return Response({"detail": "No available drivers found."},
                            status=status.HTTP_404_NOT_FOUND)

        driver_user = driver['user']
        distance_to_driver = driver['distance']

        # Calculate estimated time
        time_to_location = estimated_time(distance_to_driver)

        # Prepare data
        data = request.data.copy()
        data['customer'] = user.id
        data['pickup_location'] = json.dumps({
            "id": str(latest_location.id),
            "address":latest_location.address,
            "latitude":latest_location.latitude,
            "longitude":latest_location.longitude
        })
        data['driver'] = driver['user'].id
        data['time_minutes'] = time_to_location
        data['distance_km'] = round(distance_to_driver,2)

        serializer = ServiceRequestSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            response_data = {
                'driver': {
                    'id': driver_user.id,
                    'username': driver_user.username,
                    'plate': driver_user.plate,
                },
                'estimated_time_minutes': time_to_location
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)