import datetime
from django.core.mail import EmailMessage
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
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
    Color,
    ThoughtTheme,
    Dimension,
    ProductDimensions,
    ProductSpecification,
    FrameType,
)
import uuid
from helpers.system_variables import TAX_PERCENTAGE, UNREGISTERED_USER_EMAIL
from helpers.generators import generate_tax, generate_reset_password_token
from helpers.defaults import (
    product_type_default,
    product_grade_default,
    product_color_default,
)


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
        token = generate_reset_password_token()
        if not Colleague.objects.filter(email=email).exists():
            raise exceptions.ValidationError(
                "Email not found", code=status.HTTP_400_BAD_REQUEST
            )
        reset_password = ResetPassword.objects.create(
            email=email,
            token=token,
        )
        if reset_password:
            email = EmailMessage(
                subject="Password reset request",
                body=f"Follow the link to reset your password http://localhost:8000/reset?token={token}",
                from_email="oforimensahebenezer07@gmail.com",
                to=["quameophory@yahoo.com"],
            )
            email.send()
        return reset_password


class SetNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        token = self.validated_data["token"]
        new_password = self.validated_data["new_password"]
        try:
            reset_password = ResetPassword.objects.get(token=token)
            colleague = Colleague.objects.get(email=reset_password.email)
            colleague.set_password(new_password)
            colleague.save()
            reset_password.delete()
        except ResetPassword.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token")


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name"]
        read_only_fields = ["id"]


class ProductGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGrade
        fields = ["id", "name"]
        read_only_fields = ["id"]


class ThoughtThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThoughtTheme
        fields = ["id", "name"]
        read_only_fields = ["id"]


class FrameTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrameType
        fields = ["id", "name"]
        read_only_fields = ["id"]


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ["id", "added_at", "message", "user"]
        read_only_fields = ["id"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "photo", "description"]
        read_only_fields = ["id"]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name"]
        read_only_fields = ["id"]


class DimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dimension
        fields = ["id", "width", "height"]
        read_only_fields = ["id"]


class ProductDimensionSerializer(serializers.ModelSerializer):
    dimension = DimensionSerializer()
    width = serializers.IntegerField(read_only=True)
    height = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductDimensions
        fields = ["id", "dimension", "width", "height", "weight", "unit_cost"]


class ProductSpecificationSerializer(serializers.ModelSerializer):
    dimension = DimensionSerializer()
    frame_type = FrameTypeSerializer()
    color = ColorSerializer()

    class Meta:
        model = ProductSpecification
        fields = [
            "id",
            "dimension",
            "color",
            "frame_type",
            "weight",
            "unit_price",
            "qty",
        ]
        read_only_fields = ["id"]


class ProductListSerializer(serializers.HyperlinkedModelSerializer):
    product_type = serializers.SlugRelatedField(slug_field="name", read_only=True)
    grade = serializers.SlugRelatedField(slug_field="name", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    themes = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "url",
            "id",
            "name",
            "themes",
            "product_type",
            "grade",
            "images",
            "specifications",
        ]


class ProductDetailSerializer(serializers.HyperlinkedModelSerializer):
    product_type = ProductTypeSerializer(read_only=True)
    grade = ProductGradeSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    # product_dimensions = ProductDimensionSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    themes = ThoughtThemeSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "url",
            "id",
            "name",
            "product_type",
            "themes",
            "grade",
            "images",
            "description",
            "specifications",
            "reviews",
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    product_type = ProductTypeSerializer()
    grade = ProductGradeSerializer()
    images = ProductImageSerializer(many=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    themes = ThoughtThemeSerializer(many=True)
    specifications = ProductSpecificationSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_type",
            "grade",
            "themes",
            "description",
            "specifications",
            "images",
            "reviews",
            "return_policy",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data: dict):

        self.default_type, _ = ProductType.objects.get_or_create(name="Default Type")
        self.default_grade, _ = ProductGrade.objects.get_or_create(name="Default Grade")
        self.default_theme, _ = ThoughtTheme.objects.get_or_create(name="Default Theme")
        self.default_color, _ = Color.objects.get_or_create(
            name="Default Color", defaults={"code": "default"}
        )
        self.default_frame_type, _ = frame_type = FrameType.objects.get_or_create(
            name="Default Type"
        )

        product_type_data = validated_data.pop("product_type", {})
        grade_data = validated_data.pop("grade", {})
        themes_data = validated_data.pop("themes", [])
        images_data = validated_data.pop("images", [])
        specifications_data = validated_data.pop("specifications", [])

        product_type = None
        if not product_type_data:
            product_type = self.default_type
        else:
            if "name" in product_type_data:
                product_type, _ = ProductType.objects.get_or_create(
                    name=product_type_data["name"]
                )

        grade = None
        if not grade_data:
            grade = self.default_grade
        else:
            if "name" in grade_data:
                grade, _ = ProductGrade.objects.get_or_create(name=grade_data["name"])

        with transaction.atomic():
            product = Product.objects.create(
                product_type=product_type,
                grade=grade,
                **validated_data,
            )

            thought_themes = []
            if not themes_data:
                thought_themes.append(self.default_theme)
            else:
                thought_themes = [
                    ThoughtTheme.objects.get_or_create(name=theme_data["name"])[0]
                    for theme_data in themes_data
                    if "name" in theme_data
                ]

            product.themes.set(thought_themes)

            # Create images and link to product
            ProductImage.objects.bulk_create(
                [
                    ProductImage(product=product, **image_data)
                    for image_data in images_data
                ]
            )

            if specifications_data:
                for specification_data in specifications_data:
                    dimension_data = specification_data.pop("dimension", {})
                    dimension = (
                        None
                        if not dimension_data
                        else Dimension.objects.create(**dimension_data)
                    )

                    color_data = specification_data.pop("color", {})
                    color = (
                        self.default_color
                        if not color_data
                        else Color.objects.create(**color_data)
                    )

                    frame_type_data = specification_data.pop("frame_type", {})
                    frame_type = (
                        self.default_frame_type
                        if not frame_type_data
                        else FrameType.objects.create(**frame_type_data)
                    )

                    ProductSpecification.objects.create(
                        product=product,
                        dimension=dimension,
                        color=color,
                        frame_type=frame_type,
                        **specification_data,
                    )
            return product

    def update(self, instance, validated_data):
        product_type_data = validated_data.pop("product_type", {})
        grade_data = validated_data.pop("grade", {})
        themes_data = validated_data.pop("themes", [])
        images_data = validated_data.pop("images", [])
        specifications_data = validated_data.pop("specifications", [])

        product_type = None
        if not product_type_data:
            product_type = self.default_type
        else:
            if "name" in product_type_data:
                product_type, _ = ProductType.objects.get_or_create(
                    name=product_type_data["name"]
                )

        grade = None
        if not grade_data:
            grade = self.default_grade
        else:
            if "name" in grade_data:
                grade, _ = ProductGrade.objects.get_or_create(name=grade_data["name"])

        with transaction.atomic():
            instance.name = validated_data.get("name", instance.name)
            instance.product_type = product_type
            instance.grade = grade

            thought_themes = []
            if not themes_data:
                thought_themes.append(self.default_theme)
            else:
                thought_themes = [
                    ThoughtTheme.objects.get_or_create(name=theme_data["name"])[0]
                    for theme_data in themes_data
                    if "name" in theme_data
                ]

            instance.themes.set(thought_themes)

            ProductImage.objects.bulk_create(
                [
                    ProductImage(product=instance, **image_data)
                    for image_data in images_data
                ]
            )
            instance.description = validated_data.get("description", "")

            if specifications_data:
                for specification_data in specifications_data:
                    dimension_data = specification_data.pop("dimension", {})
                    dimension = (
                        None
                        if not dimension_data
                        else Dimension.objects.create(**dimension_data)
                    )

                    color_data = specification_data.pop("color", {})
                    color = (
                        self.default_color
                        if not color_data
                        else Color.objects.create(**color_data)
                    )

                    frame_type_data = specification_data.pop("frame_type", {})
                    frame_type = (
                        self.default_frame_type
                        if not frame_type_data
                        else FrameType.objects.create(**frame_type_data)
                    )

                    ProductSpecification.objects.create(
                        product=instance,
                        dimension=dimension,
                        color=color,
                        frame_type=frame_type,
                        **specification_data,
                    )
            return instance


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
