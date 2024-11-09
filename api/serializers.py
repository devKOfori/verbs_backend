from rest_framework import exceptions
from rest_framework import serializers
from rest_framework import status
from .models import (
    Colleague,
    ProductType,
    ProductGrade,
    Product,
    ProductReview,
    ProductImage,
    Order,
    OrderItems,
    OrderStatus,
    ResetPassword,
)
import uuid
from helpers.system_variables import TAX_PERCENTAGE, UNREGISTERED_USER_EMAIL
from helpers.generators import generate_tax, generate_reset_password_token


class CreateColleagueSerializer(serializers.ModelSerializer):
    # confirm_password = serializers.CharField(write_only=True, max_length=255)
    password = serializers.CharField(write_only=True, max_length=255)

    class Meta:
        model = Colleague
        fields = ["email", "password"]

    def create(self, validated_data: dict):
        # validated_data.pop("confirm_password")
        colleague = Colleague.objects.create_user(
            validated_data["email"], validated_data["password"]
        )
        return colleague

    # def validate(self, data: dict):
    #     if data["password"] != data["confirm_password"]:
    #         raise exceptions.ValidationError(
    #             "Passwords are different", status.HTTP_400_BAD_REQUEST
    #         )
    #     return data


class ColleagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colleague
        exclude = ["password", "country"]


class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetPassword
        fields = ["email"]

    def create(self, validated_data):
        email = validated_data.get("email")
        if not Colleague.objects.filter(email=email).exists():
            raise exceptions.APIException("Email not found", code=status.HTTP_400_BAD_REQUEST)
        reset_password = ResetPassword.objects.create(
            email=email,
            token=generate_reset_password_token()
        )
        return reset_password

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name"]


class ProductGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGrade
        fields = ["id", "name"]


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ["id", "added_at", "message", "user"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["photo", "description"]


class ProductListSerializer(serializers.HyperlinkedModelSerializer):
    product_type = serializers.SlugRelatedField(slug_field="name", read_only=True)
    grade = serializers.SlugRelatedField(slug_field="name", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["url", "id", "name", "product_type", "grade", "unit_cost", "images"]
        depth = 1


class ProductDetailSerializer(serializers.HyperlinkedModelSerializer):
    product_type = serializers.SlugRelatedField(slug_field="name", read_only=True)
    grade = serializers.SlugRelatedField(slug_field="name", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "url",
            "id",
            "name",
            "product_type",
            "grade",
            "unit_cost",
            "images",
            "availability",
            "description",
            "specifications",
            "width",
            "height",
            "weight",
        ]
        depth = 1


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ["id", "name"]


class OrderItemsSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItems
        fields = ["product", "qty"]


class OrderListSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.SlugRelatedField(slug_field="name", read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name="order-detail",
        lookup_field="order_number",
    )

    class Meta:
        model = Order
        fields = [
            "url",
            "id",
            "order_number",
            "first_name",
            "last_name",
            "status",
            "items_cost",
            "items_count",
        ]


class OrderEditSerializer(serializers.ModelSerializer):
    items = OrderItemsSerializer(source="items", many=True)
    added_by = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "order_date",
            "added_by",
            "items",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "shipping_address",
        ]

        read_only_fields = [
            "id",
            "added_by",
            "status",
            "tax",
            "total_cost",
            "items_cost",
            "items_count",
            "shipping_country",
            "payment_status",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    products = OrderItemsSerializer(source="items", many=True)
    added_by = serializers.StringRelatedField()
    status = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "order_date",
            "added_by",
            "products",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "shipping_address",
            "status",
            "tax",
            "total_cost",
            "items_cost",
            "items_count",
        ]

        read_only_fields = [
            "id",
            "added_by",
            "status",
            "tax",
            "total_cost",
            "items_cost",
            "items_count",
            "shipping_country",
            "payment_status",
        ]

    def validate(self, data: dict):
        user = self.context["request"].user if "request" in self.context else None
        if not user or user.is_anonymous:
            if not all(
                [
                    data.get("first_name", ""),
                    data.get("last_name", ""),
                    data.get("email", ""),
                ]
            ):
                raise exceptions.ValidationError(
                    "Sign in or fill in the necessary details",
                    code=status.HTTP_400_BAD_REQUEST,
                )
        return data

    def create(self, validated_data: dict):
        user = self.context["request"].user if "request" in self.context else None
        # order_id = uuid.uuid4()
        order_items = validated_data.pop("items", [])
        if not order_items:
            raise exceptions.ValidationError(
                "No product selected.", code=status.HTTP_400_BAD_REQUEST
            )

        # handling anonymous user case
        if not user or user.is_anonymous:
            print(UNREGISTERED_USER_EMAIL)
            user, _ = Colleague.objects.get_or_create(
                email=UNREGISTERED_USER_EMAIL,
                defaults={"first_name": "Anonymous", "last_name": "User"},
            )
        order = Order.objects.create(
            added_by=user, items_count=len(order_items), **validated_data
        )
        # adding items purchased to order
        items_cost = 0
        items_tax = 0
        for order_item in order_items:
            item_cost = 0
            product = order_item.get("product")
            qty = order_item.get("qty")
            try:
                product_price = product.unit_cost
                item_cost = product_price * qty
                item_tax = generate_tax(item_cost, TAX_PERCENTAGE)
                OrderItems.objects.create(
                    order=order,
                    product=product,
                    qty=qty,
                    tax=item_tax,
                    cost=item_cost,
                )
                items_cost += item_cost
                items_tax += item_tax
            except Product.DoesNotExist:
                print(f"Unable to save product wit id {product.id}")
        order.items_cost = items_cost
        order.tax = items_tax
        order.save()
        return order
