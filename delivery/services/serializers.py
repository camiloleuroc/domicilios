from rest_framework import serializers
from .models import User, Location, ServiceRequest

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'is_driver')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            is_driver=validated_data.get('is_driver', False)
        )
        return user

class LocationSerializer(serializers.ModelSerializer):
    """Serializer for location data"""
    class Meta:
        model = Location
        fields = ('id', 'user', 'address', 'latitude', 'longitude', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        location = Location.objects.create(**validated_data)
        return location
    
    @classmethod
    def get_user_location(cls, user):
        """Fetches all locations associated with the provided user."""
        return Location.objects.filter(user=user)

class ServiceRequestSerializer(serializers.ModelSerializer):
    """Serializer for service requests"""
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    driver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = ServiceRequest
        fields = ('id', 'customer', 'pickup_location', 'driver', 'distance_km', 'time_minutes', 'is_completed', 'created_at')
        read_only_fields = ('id', 'created_at', 'is_completed')

    def create(self, validated_data):
        service = ServiceRequest.objects.create(**validated_data)
        return service
