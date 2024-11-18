from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Colleague, ResetPassword
from oauth2_provider.models import Application
from datetime import datetime, timedelta
import uuid
import requests
from dotenv import load_dotenv
import os

load_dotenv("../.env")


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
        data = {"email": "testuser@gmail.com", "password": "testpass123"}
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_colleague_login_incorrect_data(self):
        data = {
            "email": "testuser@gmail.com",
            "password": "testpass123.",  # wrong password
        }
        response = self.client.post(self.token_url, data)
        print(response.data)
        self.assertEqual(response.status_code, 401)


class ResetPasswordTests(APITestCase):
    def setUp(self):
        # self.url = reverse("reset-password")
        self.colleague = Colleague.objects.create_user(
            email="testuseremail@testdomain.com", password="secret"
        )
        self.reset_password = ResetPassword.objects.create(
            email="testuseremail@testdomain.com", token="2124487e263z"
        )

    def test_reset_password_valid_email(self):
        url = reverse("reset-password")
        data = {"email": "testuseremail@testdomain.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_reset_password_invalid_email(self):
        url = reverse("reset-password")
        data = {"email": "testuseremaiiiil@testdomain.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_reset_password_valid_token(self):
        reset_password = ResetPassword.objects.get(token="2124487e263z")
        url = reverse("reset-password-token", kwargs={"token": reset_password.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reset_password_invalid_token(self):
        invalid_token = "2124487e263zzz"
        url = reverse("reset-password-token", kwargs={"token": invalid_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_reset_password_expired_token(self):
        reset_password = ResetPassword.objects.get(token="2124487e263z")
        reset_password.created_at = reset_password.created_at + timedelta(hours=-11)
        reset_password.save()
        url = reverse("reset-password-token", kwargs={"token": reset_password.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

class ProductTests(APITestCase):
    def setUp(self):
        # Mock token setup
        self.token = os.getenv("TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.token['access']}",
            "Content-Type": "application/json",
        }

    def test_create_product_with_login_user(self):
        url = reverse("create-product")
        id = str(uuid.uuid4())
        product_name = f"Product - {id}"
        payload = {
            "id": id,
            "name": product_name,
            "product_type": {
                "id": "49545acb-1121-4719-8abb-ea83cb66df22",
                "name": "frame",
            },
            "grade": {
                "id": "45d39f49-8d15-4276-8c75-fcaf5117dbf1",
                "name": "essential",
            },
            "themes": [
                {"id": "37e69a08-bfba-4ef9-93ec-9844e683b643", "name": "purpose"}
            ],
            "sizes": [
                {
                    "id": "244890fe-8078-42fd-b0da-ede02814549f",
                    "width": "10.00",
                    "height": "10.00",
                }
            ],
            "weight": "10.00",
            "colors": [{"id": "1ab181d8-2d58-4f20-9b07-84fc4958d35e", "name": "brown"}],
            "frame_types": [
                {"id": "79273154-b151-4cd7-8936-ce5913a4bd2d", "name": "wood"}
            ],
            "unit_price": "3000.00",
            "qty": 5,
            "description": product_name,
            "images": [],
            "return_policy": "",
        }

        response = self.client.post(url, data=payload, format='json', **self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['name'], product_name)