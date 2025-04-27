from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Location
from rest_framework_simplejwt.tokens import RefreshToken

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
        self.assertTrue(user.check_password(self.user_data['password']))

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