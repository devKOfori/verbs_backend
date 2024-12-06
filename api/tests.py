import requests
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
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
            "first_name": "Test",
            "last_name": "User",
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


# class ProductTests(APITestCase):

#     def test_create_product_with_auth_user(self):
#         url = reverse("create-product")
#         tokens = {
#             "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMTkxOTEzNywiaWF0IjoxNzMxODMyNzM3LCJqdGkiOiIwZjJlNDI0ZjE0N2M0M2U5YmFkMDY3NGIyZGZjOTIyYSIsInVzZXJfaWQiOiJiZThlNjhkOC1jMTQ4LTQ3MGItYjJlZS1kMTQzZTI0NzlkOWEifQ.XdR997XH6E7MeTlbMWXhYDDLJUV2uEe8xkBR0j3KwcM",
#             "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxODMzMDM3LCJpYXQiOjE3MzE4MzI3MzcsImp0aSI6IjkwZDgzOWFjNmMxYjRmYTY4NTNiN2VkMjk3OTJhYTk5IiwidXNlcl9pZCI6ImJlOGU2OGQ4LWMxNDgtNDcwYi1iMmVlLWQxNDNlMjQ3OWQ5YSJ9.yOzXgdJJjeoE17bKW1YcnT_6hIgr4VN2yw_DBKTAa-o",
#         }
#         payload = {
#             "name": "",
#             "product_type": {"name": ""},
#             "grade": {"name": ""},
#             "themes": [],
#             "sizes": [],
#             "weight": 0,
#             "colors": [],
#             "frame_types": [],
#             "unit_price": 0.00,
#             "qty": 1,
#             "description": "",
#             "images": [],
#             "return_policy": "",
#         }
#         response = self.client.post(
#             url,
#             data=payload,
#             content_type="application/json",
#             headers={"Authorization": f"Bearer {tokens.get("access")}"},
#         )


class OrderTests(APITestCase):
    def setUp(self) -> None:
        pass

    # def test_create_order(self):
    #     url = reverse("create-order")
    #     data = {
    #         "items": [{"id": "94525212-c4ce-4fa5-9743-ce4e6695f8ee", "qty": 1}],
    #         "order_date": "2024-11-15",
    #         "promo_code": {"code": ""},
    #         "shipping_info": {"shipping_address": "pursitie 7 F"},
    #         "first_name": "Ebenezer",
    #         "last_name": "Ofori-Mensah",
    #         "email": "oforimensahebenezer07@gmail.com"
    #     }
    #     response = self.client.post(
    #         path=url, data=data, content_type="application/json"
    #     )
    #     print(response.data)
    #     self.assertEqual(response.status_code, 201)
