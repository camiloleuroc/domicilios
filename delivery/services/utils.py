import math
from .models import Location

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the Haversine distance between two points (in kilometers)."""

    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def estimated_time(distance_km):
    """Calculate estimated time (in minutes) assuming an average speed of 30km/h."""
    avg_speed_kmh = 30
    time_hours = distance_km / avg_speed_kmh
    time_minutes = int(time_hours * 60)

    return max(time_minutes, 1)

def nearest_driver(pickup_latitude, pickup_longitude):
        """Find the nearest driver based on the pickup location."""

        # Bring only the addresses of the most recent drivers.
        drivers = (
            Location.objects
            .filter(user__is_driver=True)
            .order_by('user', '-created_at')
            .distinct('user')
        )

        if not drivers.exists():
            return None

        driver_selected = min(
            drivers,
            key=lambda location: haversine_distance(
                pickup_latitude, pickup_longitude,
                location.latitude, location.longitude
            )
        )

        distance_to_driver = haversine_distance(
            pickup_latitude, pickup_longitude,
            driver_selected.latitude, driver_selected.longitude
        )

        return {
            'user': driver_selected.user,
            'latitude': driver_selected.latitude,
            'longitude': driver_selected.longitude,
            'distance': distance_to_driver
        }

def get_latest_user_location(user):
    """Get the latest location of the user."""
    return (
        Location.objects
        .filter(user=user)
        .order_by('-created_at')
        .first()
    )