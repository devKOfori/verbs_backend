import pytz
from .models import Colleague, Product, ResetPassword, Order
from .serializers import (
    CreateColleagueSerializer,
    ColleagueSerializer,
    ProductListSerializer,
    ProductSerializer,
    OrderSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderEditSerializer,
    ResetPasswordSerializer,
    SetNewPasswordSerializer,
)
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions, exceptions, status
from datetime import datetime, timedelta
from helpers.defaults import TOKEN_EXPIRY_HOURS
import django_filters
from django_filters import rest_framework as filters

# Create your views here.


class RegisterColleague(generics.CreateAPIView):
    queryset = Colleague.objects.all()
    serializer_class = CreateColleagueSerializer


class ColleagueList(generics.ListAPIView):
    queryset = Colleague.objects.all()
    serializer_class = ColleagueSerializer
    # permission_classes = [permissions.IsAuthenticated]


class ColleagueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Colleague.objects.all()
    serializer_class = ColleagueSerializer
    exclude = ["password", "country"]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]


def is_past_hours(datetime_field, hours):
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

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        try:
            reset_password = ResetPassword.objects.get(token=token)
            if is_past_hours(reset_password.created_at, TOKEN_EXPIRY_HOURS):
                raise exceptions.ValidationError(
                    "Token has expired. Request a new token"
                )
            return Response({"message": "valid token"}, status=status.HTTP_200_OK)
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


# class OrderEdit(generics.UpdateAPIView):
#     serializer_class = OrderEditSerializer
#     queryset = Order.objects.all()
#     lookup_field = "order_number"
#     lookup_url_kwarg = "order_number"
