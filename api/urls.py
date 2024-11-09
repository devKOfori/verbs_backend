from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    path("register/", views.RegisterColleague.as_view(), name="register"),
    path("users/", views.ColleagueList.as_view()),
    path("users/<uuid:pk>/", views.ColleagueDetail.as_view()),
    path("products/", views.ProductList.as_view()),
    path("products/<uuid:pk>/", views.ProductDetail.as_view(), name="product-detail"),
    path("orders/", views.OrderList.as_view()),
    path("orders/add/", views.OrderCreate.as_view()),
    path(
        "orders/<str:order_number>/", views.OrderDetail.as_view(), name="order-detail"
    ),
    path(
        "orders/<str:order_number>/edit", views.OrderEdit.as_view(), name="order-edit"
    ),
]
urlpatterns = format_suffix_patterns(urlpatterns)
