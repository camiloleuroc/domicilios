from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

class UserRegistrationTestCase(TestCase):
    
    def setUp(self):
        """
        Data configuration for the test case.
        """
        self.url = reverse('register')
        self.user_data = {
            'username': 'testuser',
            'password': 'password123',
            'is_driver': False
        }

    def test_register_user(self):
        """
        Verifies that the user's registration works.
        """
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
        """
            Data configuration for the test case.
        """
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
        """
            Verifies that the login with valid credentials returns JWT tokens.
        """
        response = self.client.post(self.login_url, self.user_data, format='json')

        #  Verifies that the response code is 200 OK.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verifies that the tokens is present in the response data.
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_login_with_invalid_credentials(self):
        """
         Verifies that the login with wrong credentials.
        """
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
        """
         Verifies that the login return error if dont send the username.
        """
        response = self.client.post(self.login_url, {
            'password': self.user_data['password']
        }, format='json')

        #  Verifies that the response code be 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #  Verifies that the field 'username' is in the errors.
        self.assertIn('Username and password are mandatory.', response.data['detail'])

    def test_login_missing_password(self):
        """
         Verifies that the login return error if dont send the password.
        """
        response = self.client.post(self.login_url, {
            'username': self.user_data['username']
        }, format='json')

        #  Verifies that the response code be 400 Bad Request.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #  Verifies that the field 'password' is in the errors.
        self.assertIn('Username and password are mandatory.', response.data['detail'])