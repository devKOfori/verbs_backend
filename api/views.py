import pytz
from .models import (
    Colleague,
    Product,
    ResetPassword,
    Order,
    PaymentInfo,
    ConfirmationCodeStatus,
)
from .serializers import (
    CreateColleagueSerializer,
    ColleagueSerializer,
    ProductListSerializer,
    ProductSerializer,
    OrderSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderEditSerializer,
    PaymentInfoSerializer,
    ResetPasswordSerializer,
    SetNewPasswordSerializer,
)
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions, exceptions, status
from rest_framework.views import APIView
from datetime import datetime, timedelta
from helpers.defaults import TOKEN_EXPIRY_HOURS
import django_filters
from django_filters import rest_framework as filters
import os
import subprocess
from django.http import JsonResponse, HttpResponseBadRequest


# Create your views here.


class RegisterColleague(generics.CreateAPIView):
    queryset = Colleague.objects.all()
    serializer_class = CreateColleagueSerializer


class ConfirmRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        SUCCESS_MESSAGE = "Account confirmed successfully."
        INVALID_CODE_MESSAGE = "Invalid confirmation code."
        ACCOUNT_NOT_FOUND_MESSAGE = "No account exists with the provided email."

        email = request.data.get("email")
        confirmation_code = request.data.get("confirmation_code")

        print(f"confirmation_code: {confirmation_code}")

        if not email or not confirmation_code:
            return Response(
                {"error": "Email and confirmation code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get the "Valid" status object
            valid_status = ConfirmationCodeStatus.objects.get(name="Valid")
        except ConfirmationCodeStatus.DoesNotExist:
            return Response(
                {"error": "Configuration error: Valid status not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # Get the "Invalid" status object
            invalid_status = ConfirmationCodeStatus.objects.get(name="Invalid")
        except ConfirmationCodeStatus.DoesNotExist:
            return Response(
                {"error": "Configuration error: Invalid status not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # Retrieve the account
            registered_account = Colleague.objects.get(email=email)
            print(f"confirmation_status: {registered_account.confirmation_code_status}")
        except Colleague.DoesNotExist:
            return Response(
                {"error": ACCOUNT_NOT_FOUND_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check the confirmation code and status
        if (
            registered_account.confirmation_code == confirmation_code
            and registered_account.confirmation_code_status == valid_status
        ):
            registered_account.is_account_confirmed = True
            registered_account.confirmation_code_status = invalid_status
            registered_account.save()
            return Response({"message": SUCCESS_MESSAGE}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": INVALID_CODE_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )


def github_webhook(request):
    if request.method == "POST":
        # Validate GitHub signature (recommended for security)
        event = request.headers.get("X-GitHub-Event", "ping")
        if event == "push":
            repo_dir = "/home/verbsmerch/"
            commands = [
                f"cd {repo_dir}",
                "git fetch origin",
                "git reset --hard origin/main",
                "source /home/verbsmerch/.virtualenvs/verbs_venv/bin/activate && pip install -r requirements.txt",
                "touch /var/www/verbsmerch_pythonanywhere_com_wsgi.py",  # Reload the app
            ]
            for command in commands:
                subprocess.run(command, shell=True, check=True)
            return JsonResponse({"message": "Code updated successfully"})
        return JsonResponse({"message": "Unhandled event"}, status=400)


class ColleagueList(generics.ListAPIView):
    queryset = Colleague.objects.all()
    serializer_class = ColleagueSerializer
    # permission_classes = [permissions.IsAuthenticated]


class ColleagueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Colleague.objects.all()
    serializer_class = ColleagueSerializer
    exclude = ["password", "country"]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]


def is_token_expired(datetime_field, hours):
    """
    Check if the datetime_field is past the specified number of hours from the current time.

    :param datetime_field: The datetime to check.
    :param hours: The number of hours to check against.
    :return: True if the datetime_field is past the specified hours, False otherwise.
    """
    current_time = datetime.now(pytz.utc)
    if datetime_field.tzinfo is None:
        datetime_field = pytz.utc.localize(datetime_field)
    time_difference = current_time - datetime_field
    print(current_time, datetime_field, time_difference)
    return time_difference > timedelta(hours=hours)


class ResetPasswordView(generics.CreateAPIView):
    queryset = ResetPassword.objects.all()
    serializer_class = ResetPasswordSerializer


class ResetPasswordTokenView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    queryset = ResetPassword.objects.all()

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        try:
            reset_password = ResetPassword.objects.get(token=token)
            if is_token_expired(reset_password.created_at, TOKEN_EXPIRY_HOURS):
                raise exceptions.ValidationError(
                    "Token has expired. Request a new token"
                )
            return Response(
                {"message": "Valid token. Continue to login."},
                status=status.HTTP_200_OK,
            )
        except ResetPassword.DoesNotExist:
            raise exceptions.ValidationError(
                "Token does not exist", code=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request, *args, **kwargs):
        token = kwargs.get("token")
        data = request.data.copy()
        data["token"] = token
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"message": "Password has been reset successfully"},
                status=status.HTTP_200_OK,
            )
        except exceptions.ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductFilter(django_filters.FilterSet):
    unit_price = django_filters.RangeFilter()

    class Meta:
        model = Product
        fields = {
            "name": ["exact"],
            "grade__name": ["exact"],
            "themes__name": ["exact"],
            "sizes__width": ["lte", "gte"],
            "sizes__height": ["lte", "gte"],
            "weight": ["lte", "gte"],
            "colors__name": ["exact"],
        }


class ProductList(generics.ListAPIView):
    serializer_class = ProductListSerializer
    queryset = Product.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductCreate(generics.CreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class OrderList(generics.ListAPIView):
    serializer_class = OrderListSerializer
    queryset = Order.objects.all()


class OrderCreate(generics.CreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class OrderDetail(generics.RetrieveDestroyAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_field = "order_number"
    lookup_url_kwarg = "order_number"


class OrderPayment(generics.CreateAPIView):
    serializer_class = PaymentInfoSerializer
    queryset = PaymentInfo.objects.all()


# class OrderEdit(generics.UpdateAPIView):
#     serializer_class = OrderEditSerializer
#     queryset = Order.objects.all()
#     lookup_field = "order_number"
#     lookup_url_kwarg = "order_number"
