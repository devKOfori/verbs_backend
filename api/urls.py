from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    path("register/", views.RegisterColleague.as_view(), name="register"),
    path("confirm-registration/", views.ConfirmRegistrationView.as_view(), name="confirm-register"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path(
        "reset-password/<str:token>/",
        views.ResetPasswordTokenView.as_view(),
        name="reset-password-token",
    ),
    path("users/", views.ColleagueList.as_view()),
    path("users/<uuid:pk>/", views.ColleagueDetail.as_view()),
    path("products/", views.ProductList.as_view()),
    path("products/add/", views.ProductCreate.as_view(), name="create-product"),
    path("products/<uuid:pk>/", views.ProductDetail.as_view(), name="product-detail"),
    path("orders/", views.OrderList.as_view()),
    path("orders/add/", views.OrderCreate.as_view(), name="create-order"),
    path(
        "orders/<str:order_number>/", views.OrderDetail.as_view(), name="order-detail"
    ),
    path("orders/<str:order_number>/pay/", views.OrderPayment.as_view(), name="order-payment"),
    # path(
    #     "orders/<str:order_number>/edit/", views.OrderEdit.as_view(), name="order-edit"
    # ),
    path('github-webhook/', views.github_webhook, name='github_webhook'),
]
urlpatterns = format_suffix_patterns(urlpatterns)
