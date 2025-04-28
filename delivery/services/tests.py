from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Location, ServiceRequest
from rest_framework_simplejwt.tokens import RefreshToken
import json

class UserRegistrationTestCase(TestCase):
    
    def setUp(self):
        """Data configuration for the test case."""

        self.url = reverse('register')
        self.user_data = {
            'username': 'testuser',
            'password': 'password123',
            'is_driver': False
        }

    def test_register_user(self):
        """Verifies that the user's registration works."""

        response = self.client.post(self.url, self.user_data, format='json')

        # Verifies that the response be 201 Created.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifies that the username and another data be correct.
        self.assertEqual(response.data['username'], self.user_data['username'])
        self.assertIn('id', response.data) 
        self.assertEqual(response.data['is_driver'], self.user_data['is_driver'])

        # Verifies that the user exists in the database.
        User = get_user_model()
        user = User.objects.get(username=self.user_data['username'])
        self.assertIsNotNone(user)

class LoginTestCase(TestCase):

    def setUp(self):
        """Data configuration for the test case."""

        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'password': 'password123'
        }

        # Created a user for testing.
        user = get_user_model().objects.create_user(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        user.save()

    def test_login_with_valid_credentials(self):
        """Verifies that the login with valid credentials returns JWT tokens."""

        response = self.client.post(self.login_url, self.user_data, format='json')

        #  Verifies that the response code is 200 OK.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verifies that the tokens is present in the response data.
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_login_with_invalid_credentials(self):
        """Verifies that the login with wrong credentials."""

        invalid_user_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, invalid_user_data, format='json')

        #  Verifies that the response code be 401 Unauthorized.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        #  Verifies that the message error be 'Invalid credentials.'
        self.assertEqual(response.data['detail'], 'Invalid credentials.')

    def test_login_missing_username(self):
        """Verifies that the login return error if dont send the username."""

        response = self.client.post(self.login_url, {
            'password': self.user_data['password']
        }, format='json')

        #  Verifies that the response code be 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #  Verifies that the field 'username' is in the errors.
        self.assertIn('Username and password are mandatory.', response.data['detail'])

    def test_login_missing_password(self):
        """Verifies that the login return error if dont send the password."""

        response = self.client.post(self.login_url, {
            'username': self.user_data['username']
        }, format='json')

        #  Verifies that the response code be 400 Bad Request.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #  Verifies that the field 'password' is in the errors.
        self.assertIn('Username and password are mandatory.', response.data['detail'])

class LocationAssignViewTestCase(TestCase):
    
    def setUp(self):
        """Data configuration for the test case."""
        
        self.user = get_user_model().objects.create_user(
            username='testuser', 
            password='password123'
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        self.client = APIClient()
        self.location_url = reverse('locations')
        self.location_data = {
            'address': 'Ciudad techo av americas # 80G',
            'latitude': 4.63766,
            'longitude': -74.1536698
        }

        self.login_url = reverse('login')
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')

        self.access_token = response.data['access_token']

        self.update_data = {
            'address': 'New Address',
            'latitude': 40.63800,
            'longitude': -75.154000
        }

        self.partial_update_data = {
            'address': 'Partial Address'
        }

    def test_create_location(self):
        """Checks the location creation for the authenticated user."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        response = self.client.post(self.location_url, self.location_data, format='json')
        
        # Verifies that the response code be 201 Created.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verifies that the location has been successfully created.
        self.assertEqual(response.data['address'], self.location_data['address'])
        self.assertEqual(response.data['latitude'], self.location_data['latitude'])
        self.assertEqual(response.data['longitude'], self.location_data['longitude'])
        
        # Verifies that the location is associated with the authenticated user.
        location = Location.objects.get(id=response.data['id'])
        self.assertEqual(location.user, self.user)

    def test_create_location_without_token(self):
        """Verify that an unauthenticated user cannot create a location."""

        response = self.client.post(self.location_url, self.location_data, format='json')

        # Verifies that the response code be 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_locations(self):
        """Check that an authenticated user can query their locations."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        # Creates a location for the user.
        Location.objects.create(user=self.user, address='Parque Timiza', latitude=4.610819, longitude=-74.156850)
        Location.objects.create(user=self.user, address='Monserrate', latitude=4.6519715, longitude=-74.1771823)

        # GET request to query the locations of the authenticated user.
        response = self.client.get(self.location_url, format='json')
        
        # Verifies that the response be 200 OK.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the response contains the locations created.
        self.assertEqual(len(response.data), 2)  # Espera dos ubicaciones
        self.assertEqual(response.data[0]['address'], 'Parque Timiza')
        self.assertEqual(response.data[1]['address'], 'Monserrate')

    def test_get_user_locations_no_locations(self):
        """Check that if the user has no locations, an appropriate message is returned."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        # GET request to query the locations of the authenticated user.
        response = self.client.get(self.location_url, format='json')
        
        # Verifies that the response be 404 Not Found.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verifies that the message in the response is ok.
        self.assertEqual(response.data['detail'], 'No locations found.')
    
    def test_put_location_success(self):
        """Check full update of a location with authentication."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        # Create a location for the user.
        response = self.client.post(self.location_url, self.location_data, format='json')

        response = self.client.put(self.location_url+str(response.data['id']) + '/', self.update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], self.update_data['address'])
        self.assertEqual(response.data['latitude'], self.update_data['latitude'])
        self.assertEqual(response.data['longitude'], self.update_data['longitude'])

    def test_put_location_unauthenticated(self):
        """Check full update of a location without authentication."""

        response = self.client.put(self.location_url, self.update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_location_success(self):
        """Check partial update of a location with authentication."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        # Create a location for the user.
        response_location = self.client.post(self.location_url, self.location_data, format='json')

        response = self.client.patch(self.location_url+str(response_location.data['id']) + '/', self.partial_update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], self.partial_update_data['address'])

    def test_patch_location_unauthenticated(self):
        """Check partial update of a location without authentication."""

        response = self.client.patch(self.location_url, self.partial_update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_location_success(self):
        """Check deletion of a location with authentication."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        # Create a location for the user.
        response_location = self.client.post(self.location_url, self.location_data, format='json')
        
        # Delete a location for the user.
        response = self.client.delete(self.location_url+str(response_location.data['id']) + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Location.objects.filter(id=str(response_location.data['id'])).exists())

    def test_delete_location_unauthenticated(self):
        """Check deletion of a location without authentication."""
        
        response = self.client.delete(self.location_url+str("876342d4-2dae-4712-a107-6c5028ca0153") + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ServiceRequestTestCase(TestCase):
    
    def setUp(self):
        """Data configuration for the test case."""

        self.client = APIClient()

        self.login_url = reverse('login')

        self.customer = get_user_model().objects.create_user(
            username='customer1',
            password='password123',
            is_driver=False
        )
        
        response = self.client.post(self.login_url, {
                    'username': 'customer1',
                    'password': 'password123'
                }, format='json')
        
        self.access_token_customer = response.data['access_token']
        
        self.driver_first = get_user_model().objects.create_user(
            username='driver1',
            password='password123',
            is_driver=True
        )

        response = self.client.post(self.login_url, {
                    'username': 'driver1',
                    'password': 'password123'
                }, format='json')
        
        self.access_token_driver = response.data['access_token']

        self.driver_second = get_user_model().objects.create_user(
            username='driver2',
            password='password123',
            is_driver=True
        )

        # Location for the customer
        self.customer_location = Location.objects.create(
            user=self.customer,
            address='test Address',
            latitude=10.0,
            longitude=10.0
        )

        # Location for the first driver
        self.driver_first_location = Location.objects.create(
            user=self.driver_first,
            address='Driver First Address',
            latitude=12.1,
            longitude=12.1
        )

        # Location for the second driver
        self.driver_second_location = Location.objects.create(
            user=self.driver_second,
            address='Driver Second Address',
            latitude=9.1,
            longitude=9.1
        )

        self.url = reverse('delivery')

    def test_create_service_request_success(self):
        """Check successful creation of a service request by a non-driver user."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token_customer)

        data = {}  # No pickup_location is sent, the view picks it up automatically.

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['driver']['username'], self.driver_second.username)
        self.assertIsNotNone(response.data['estimated_time_minutes'])

    def test_driver_cannot_create_service_request(self):
        """Check that a driver cannot create a service request."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token_driver)

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Drivers cannot create service requests.', str(response.data))

    def test_create_service_request_without_location(self):
        """Check failure when customer has no location."""

        user_without_location = get_user_model().objects.create_user(
            username='no_location_user',
            password='password123',
            is_driver=False
        )

        response = self.client.post(self.login_url, {
                    'username': 'no_location_user',
                    'password': 'password123'
                }, format='json')
        
        access_token = response.data['access_token']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('must have at least one location', str(response.data))

    def test_create_service_request_without_available_drivers(self):
        """Check failure when no drivers are available."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token_customer)

        # Delete all drivers
        get_user_model().objects.filter(is_driver=True).delete()

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No available drivers', str(response.data))

class CloseServiceRequestTest(TestCase):

    def setUp(self):
        """Data configuration for the test case."""
        
        self.client = APIClient()
        self.login_url = reverse('login')
        self.endservice_url = reverse('endservice')

        # Create a customer user
        self.customer = get_user_model().objects.create_user(
            username="customer1",
            password="password123",
            is_driver=False
        )

        response = self.client.post(self.login_url, {
                    'username': 'customer1',
                    'password': 'password123'
                }, format='json')
        
        self.access_token_customer = response.data['access_token']

        # Create a driver user
        self.driver = get_user_model().objects.create_user(
            username="driver1",
            password="password123",
            is_driver=True
        )

        response = self.client.post(self.login_url, {
                    'username': 'driver1',
                    'password': 'password123'
                }, format='json')
        
        self.access_token_driver = response.data['access_token']

        # Create a service request assigned to the driver (with the customer)
        self.service_request = ServiceRequest.objects.create(
            customer=self.customer,
            driver=self.driver,
            pickup_location=json.dumps({
                "id": "12345678-1234-5678-1234-123456789012",
                "address":"Test Address",
                "latitude":4.610819,
                "longitude":-74.156850
            }),
            time_minutes=15,
            distance_km=10,
            is_completed=False
        )        

    def test_close_service_request_customer(self):
        """Check that the customer can close their active service request."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token_customer)

        response = self.client.post(self.endservice_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ServiceRequest.objects.get(id=self.service_request.id).is_completed)

        # Ensure that the close_service_at field is updated and in ISO format
        close_service_at = ServiceRequest.objects.get(id=self.service_request.id).close_service_at
        self.assertEqual(str(response.data['id']), str(self.service_request.id))
        self.assertEqual(response.data['close_service_at'], close_service_at.isoformat())

    def test_close_service_request_driver(self):
        """Check that the driver can close their active service request."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token_driver)

        response = self.client.post(self.endservice_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ServiceRequest.objects.get(id=self.service_request.id).is_completed)

        # Ensure that the close_service_at field is updated and in ISO format
        close_service_at = ServiceRequest.objects.get(id=self.service_request.id).close_service_at
        self.assertEqual(str(response.data['id']), str(self.service_request.id))
        self.assertEqual(response.data['close_service_at'], close_service_at.isoformat())

    def test_close_service_request_no_active_request(self):
        """Check that a user cannot close a service request if they don't have an active one."""

        # Mark the request as completed
        self.service_request.is_completed = True
        self.service_request.save()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token_customer)

        response = self.client.post(self.endservice_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "No active service request found.")

    def test_close_service_request_not_authenticated(self):
        """Check that a non-authenticated user cannot close a service request."""

        response = self.client.post(self.endservice_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

class DriverListTests(APITestCase):
    
    def setUp(self):
        """Data configuration for the test case."""

        self.client = APIClient()
        self.login_url = reverse('login')
        self.url = reverse('drivers')

        # Create a customer user
        self.customer = get_user_model().objects.create_user(
            username="customer1",
            password="password123",
            is_driver=False
        )

        response = self.client.post(self.login_url, {
                    'username': 'customer1',
                    'password': 'password123'
                }, format='json')
        
        self.access_token = response.data['access_token']

        # Create a first driver user
        self.driver1 = get_user_model().objects.create_user(
            username="driver1",
            password="password123",
            is_driver=True
        )

        # Create a second driver user
        self.driver2 = get_user_model().objects.create_user(
            username="driver2",
            password="password123",
            is_driver=True
        )
        

    def test_get_drivers_authenticated(self):
        """Check An authenticated user can get the list of drivers"""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        usernames = [driver['username'] for driver in response.data]
        self.assertIn(self.driver1.username, usernames)
        self.assertIn(self.driver2.username, usernames)

    def test_get_drivers_unauthenticated(self):
        """Check An unauthenticated user cannot access the list of drivers."""
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserDetailTestCase(APITestCase):
    def setUp(self):
        """Data configuration for the test case."""
        
        self.client = APIClient()
        self.user_detail_url = reverse('userdetail')
        self.login_url = reverse('login')

        # Create a customer user
        self.customer = get_user_model().objects.create_user(
            username="customer1",
            password="password123",
            is_driver=False
        )

        response = self.client.post(self.login_url, {
                    'username': 'customer1',
                    'password': 'password123'
                }, format='json')
        
        self.access_token = response.data['access_token']

    def test_get_user_details_authenticated(self):
        """Check retrieving user details when authenticated."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.customer.username)

    def test_get_user_details_unauthenticated(self):
        """Check retrieving user details without authentication."""

        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_details_put(self):
        """Check full update of user details."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        updated_data = {
            'username': 'newusername',
            'password': 'password123',
            'is_driver': True,
            'plate': '123qwe'
        }
        response = self.client.put(self.user_detail_url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.username, 'newusername')

    def test_partial_update_user_details_patch(self):
        """Check partial update of user details."""
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        updated_data = {
            'username': 'partialupdate',
            'password': 'password123'
        }
        response = self.client.patch(self.user_detail_url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.username, 'partialupdate')

    def test_update_user_invalid_data(self):
        """Check updating user with invalid data."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        invalid_data = {
            'username': ''  # username cannot be blank
        }
        response = self.client.put(self.user_detail_url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
    
    def test_delete_user_account(self):
        """Check deleting the authenticated user account."""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(get_user_model().objects.filter(id=self.customer.id).exists())