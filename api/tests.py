from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Colleague
from oauth2_provider.models import Application


class ColleagueRegistrationAPITests(APITestCase):
    def test_colleague_registration_api(self):
        url = reverse("register")
        data = {
            "email": "testuser@testdomain.com",
            "password": "secret",
            "confirm_password": "secret",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_registration_with_existing_username(self):
        # Create an initial user
        Colleague.objects.create_user(
            email="existinguser@testdomain.com", password="complexpassword123"
        )

        url = reverse("register")
        data = {
            "email": "existinguser@testdomain.com",
            "password": "complexpassword123",
            # 'confirm_password': 'complexpassword123',
        }
        response = self.client.post(url, data, format="json")
        # print(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["email"],
            ["Colleague with this email address already exists."],
        )

    def test_registration_with_invalid_data(self):
        url = reverse("register")
        data = {
            "password": "short",  # Example of invalid password (too short)
            "email": "not-an-email",  # Invalid email format
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)  # Expected status for bad request


class ColleagueLoginAPITests(APITestCase):
    def setUp(self):
        self.user = Colleague.objects.create_user(
            email="testuser@gmail.com", password="testpass123"
        )
        self.token_url = reverse("token_obtain_pair")

    def test_colleague_login(self):
        data = {
            "email":"testuser@gmail.com",
            "password": "testpass123"
        }
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
    
    def test_colleague_login_incorrect_data(self):
        data = {
            "email":"testuser@gmail.com",
            "password": "testpass123." #wrong password
        }
        response = self.client.post(self.token_url, data)
        print(response.data)
        self.assertEqual(response.status_code, 401)
