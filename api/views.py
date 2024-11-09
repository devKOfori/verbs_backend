from django.shortcuts import render
from .models import Colleague, Product, Order, ResetPassword
from .serializers import (
    CreateColleagueSerializer,
    ColleagueSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderEditSerializer,
    ResetPasswordSerializer
)
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView

# Create your views here.

class RegisterColleague(generics.CreateAPIView):
    queryset = Colleague.objects.all()
    serializer_class = CreateColleagueSerializer

class ColleagueList(generics.ListAPIView):
    queryset = Colleague.objects.all()
    serializer_class = ColleagueSerializer
    permission_classes = [permissions.IsAuthenticated]


class ColleagueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Colleague.objects.all()
    serializer_class = ColleagueSerializer
    exclude = ["password", "country"]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ResetPasswordView(generics.CreateAPIView):
    queryset = ResetPassword.objects.all()
    serializer_class = ResetPasswordSerializer

class ProductList(generics.ListAPIView):
    serializer_class = ProductListSerializer
    queryset = Product.objects.all()


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()


class OrderList(generics.ListAPIView):
    serializer_class = OrderListSerializer
    queryset = Order.objects.all()


class OrderCreate(generics.CreateAPIView):
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.all()


class OrderDetail(generics.RetrieveDestroyAPIView):
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.all()
    lookup_field = "order_number"
    lookup_url_kwarg = "order_number"


class OrderEdit(generics.UpdateAPIView):
    serializer_class = OrderEditSerializer
    queryset = Order.objects.all()
    lookup_field = "order_number"
    lookup_url_kwarg = "order_number"
