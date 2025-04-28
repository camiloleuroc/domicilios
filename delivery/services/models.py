import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom user model with uuid management"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_driver = models.BooleanField(default=False)
    plate = models.CharField(max_length=8, blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

class Location(models.Model):
    """Model for storing location data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class ServiceRequest(models.Model):
    """Model for delivery requested by a customer"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    pickup_location = models.JSONField()
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    distance_km = models.FloatField()
    time_minutes = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    close_at = models.DateTimeField(auto_now_add=True)