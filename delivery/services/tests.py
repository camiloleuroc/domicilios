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