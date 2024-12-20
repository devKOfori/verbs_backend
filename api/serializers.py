import datetime
from django.core.mail import EmailMessage, BadHeaderError
from django.db import transaction, IntegrityError
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
    FrameType,
    PaymentInfo,
    PaymentMethod,
    PromoCode,
    ShippingInfo,
)
import uuid
from helpers.system_variables import (
    TAX_PERCENTAGE,
    UNREGISTERED_USER_EMAIL,
    SENDER_EMAIL,
)
from helpers.generators import (
    generate_order_taxes,
    generate_reset_password_token,
    generate_shipping_cost,
    generate_registration_code,
)
from helpers.defaults import (
    product_type_default,
    product_grade_default,
    product_color_default,
    default_payment_status,
    default_confirmation_code_status,
)


class CreateColleagueSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=255)

    class Meta:
        model = Colleague
        fields = ["email", "password", "first_name", "last_name"]

    def create(self, validated_data: dict):
        confirmation_code = generate_registration_code()

        try:
            colleague = Colleague.objects.create_user(
                validated_data["email"],
                validated_data["password"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                confirmation_code=confirmation_code,
                confirmation_code_status=default_confirmation_code_status(),
                is_account_confirmed=False,
            )
        except Exception as e:
            raise serializers.ValidationError(
                f"An error occured creating colleague account {e}"
            )
        else:
            email_body = f"""
                Hi {colleague.first_name},
                Complete your registration with this one-time security code:
                {confirmation_code}
                
                Ignore this message if you have not registered with us.

                Thank you,
                Verbs Team.
            """

            email = EmailMessage(
                subject="Confirm your registration",
                body=email_body,
                from_email=SENDER_EMAIL,
                to=[colleague.email],
            )
            try:
                email.send()
            except Exception as email_error:
                raise serializers.ValidationError(
                    f"Account created but failed to send confirmation email: {email_error}"
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
            raise serializers.ValidationError(
                "Email not found", code=status.HTTP_400_BAD_REQUEST
            )
        # reset_password = ResetPassword.objects.create(
        #     email=email,
        #     token=token,
        # )
        # if reset_password:
        #     email = EmailMessage(
        #         subject="Password reset request",
        #         body=f"Follow the link to reset your password http://localhost:8000/reset?token={token}",
        #         from_email="oforimensahebenezer07@gmail.com",
        #         to=["quameophory@yahoo.com"],
        #     )
        #     email.send()
        try:
            reset_password = ResetPassword.objects.create(
                email=email,
                token=token,
            )
            email = EmailMessage(
                subject="Password reset link",
                body=f"Follow the link to reset your password http://localhost:8000/reset?token={token}. Token expires after 1 hour.",
                from_email="oforimensahebenezer07@gmail.com",
                to=["quameophory@yahoo.com"],
            )
            email.send()
        except BadHeaderError:
            print("Couldn't send email. Invalid header found.")
        except Exception as e:
            print("Couldn't create a reset password link", e)

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
        except (ResetPassword.DoesNotExist, Colleague.DoesNotExist):
            raise serializers.ValidationError("Invalid token or email")


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name"]
        # read_only_fields = ["id"]

    def to_internal_value(self, data):
        """
        Ensure that the `id` refers to an existing `ProductType`.
        """
        if isinstance(data, dict) and "id" in data:
            try:
                # Retrieve the existing ProductType instance by ID
                return ProductType.objects.get(id=data["id"])
            except ProductType.DoesNotExist:
                raise serializers.ValidationError(
                    {"id": "Invalid product type id. This product type does not exist."}
                )
        raise serializers.ValidationError({"id": "This field is required."})

    def to_representation(self, instance):
        """
        Customize the output representation for the frontend.
        """
        return {"id": instance.id, "name": instance.name}


class ProductGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGrade
        fields = ["id", "name"]
        # read_only_fields = ["id"]

    def to_internal_value(self, data):
        if isinstance(data, dict) and "id" in data:
            try:
                product_grade = ProductGrade.objects.get(id=data["id"])
                return product_grade
            except ProductGrade.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "id": "Invalid product grade id. This product grade does not exist."
                    }
                )
        raise serializers.ValidationError({"id": "This field is required."})

    def to_representation(self, instance):
        """
        Customize the output representation for the frontend.
        """
        return {"id": instance.id, "name": instance.name}


class ThoughtThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThoughtTheme
        fields = ["id", "name"]
        # read_only_fields = ["id"]

    def to_internal_value(self, data):
        if isinstance(data, dict) and "id" in data:
            try:
                thought_theme = ThoughtTheme.objects.get(id=data["id"])
                return thought_theme
            except ThoughtTheme.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "id": "Invalid thought theme id. This thought theme does not exist."
                    }
                )
        raise serializers.ValidationError({"id": "This field is required."})

    def to_representation(self, instance):
        """
        Customize the output representation for the frontend.
        """
        return {"id": instance.id, "name": instance.name}


class FrameTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrameType
        fields = ["id", "name"]
        # read_only_fields = ["id"]

    def to_internal_value(self, data):
        if isinstance(data, dict) and "id" in data:
            try:
                frame_type = FrameType.objects.get(id=data["id"])
                return frame_type
            except FrameType.DoesNotExist:
                raise serializers.ValidationError(
                    {"id": "Invalid frame type id. This frame type does not exist."}
                )
        raise serializers.ValidationError({"id": "This field is required."})
        # return data

    def to_representation(self, instance):
        """
        Customize the output representation for the frontend.
        """
        return {"id": instance.id, "name": instance.name}


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
        # read_only_fields = ["id"]

    def to_internal_value(self, data):
        if isinstance(data, dict) and "id" in data:
            try:
                color = Color.objects.get(id=data["id"])
                return color
            except Color.DoesNotExist:
                raise serializers.ValidationError(
                    {"id": "Invalid color id. This color does not exist."}
                )
        raise serializers.ValidationError({"id": "This field is required."})

    def to_representation(self, instance):
        """
        Customize the output representation for the frontend.
        """
        return {"id": instance.id, "name": instance.name}


class DimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dimension
        fields = ["id", "width", "height"]
        # read_only_fields = ["id"]

    def to_internal_value(self, data):
        if isinstance(data, dict) and "id" in data:
            try:
                dimension = Dimension.objects.get(id=data["id"])
                return dimension
            except Dimension.DoesNotExist:
                raise serializers.ValidationError(
                    {"id": "Invalid dimension id. This dimension does not exist."}
                )
        raise serializers.ValidationError({"id": "This field is required."})

    def to_representation(self, instance):
        """
        Customize the output representation for the frontend.
        """
        return {"id": instance.id, "width": instance.width, "height": instance.height}


class ProductListSerializer(serializers.HyperlinkedModelSerializer):
    product_type = serializers.SlugRelatedField(slug_field="name", read_only=True)
    grade = serializers.SlugRelatedField(slug_field="name", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    themes = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)
    sizes = DimensionSerializer(many=True)
    colors = ColorSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "url",
            "id",
            "name",
            "colors",
            "themes",
            "product_type",
            "grade",
            "images",
            "sizes",
            "unit_price",
        ]


class ProductDetailSerializer(serializers.HyperlinkedModelSerializer):
    product_type = ProductTypeSerializer(read_only=True)
    grade = ProductGradeSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    # product_dimensions = ProductDimensionSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    themes = ThoughtThemeSerializer(many=True, read_only=True)

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


class ProductDisplaySerializer(serializers.ModelSerializer):
    product_type = serializers.StringRelatedField()
    grade = serializers.StringRelatedField()
    themes = serializers.StringRelatedField(many=True)

    class Meta:
        model = Product
        fields = ["name", "product_type", "grade", "themes"]


class ProductSerializer(serializers.ModelSerializer):
    product_type = ProductTypeSerializer()
    grade = ProductGradeSerializer()
    images = ProductImageSerializer(many=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    themes = ThoughtThemeSerializer(many=True)
    colors = ColorSerializer(many=True)
    frame_types = FrameTypeSerializer(many=True)
    sizes = DimensionSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_type",
            "grade",
            "themes",
            "sizes",
            "weight",
            "colors",
            "frame_types",
            "unit_price",
            "qty",
            "description",
            "images",
            "return_policy",
            "reviews",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data: dict):
        self.default_type, _ = ProductType.objects.get_or_create(name="Default Type")
        self.default_grade, _ = ProductGrade.objects.get_or_create(name="Default Grade")
        self.default_theme, _ = ThoughtTheme.objects.get_or_create(name="Default Theme")
        self.default_color, _ = Color.objects.get_or_create(
            name="Default Color", defaults={"code": "default"}
        )
        self.default_frame_type, _ = FrameType.objects.get_or_create(
            name="Default Type"
        )

        images_data = validated_data.pop("images", [])

        product_type = validated_data.pop("product_type", None)
        grade = validated_data.pop("grade", None)
        thought_themes = validated_data.pop("themes", [])
        sizes = validated_data.pop("sizes", [])
        colors = validated_data.pop("colors", [])
        frame_types = validated_data.pop("frame_types", [])

        with transaction.atomic():
            request = self.context.get("request")
            user = request.user if request else None
            product = Product.objects.create(
                product_type=product_type,
                added_by=user,
                grade=grade,
                **validated_data,
            )

            product.themes.set(thought_themes)

            product.sizes.set(sizes)

            product.colors.set(colors)

            product.frame_types.set(frame_types)

            # Create images and link to product
            ProductImage.objects.bulk_create(
                [
                    ProductImage(product=product, **image_data)
                    for image_data in images_data
                ]
            )
            return product

    def update(self, instance, validated_data):
        product_type_data = validated_data.pop("product_type", {})
        grade_data = validated_data.pop("grade", {})
        themes_data = validated_data.pop("themes", [])
        images_data = validated_data.pop("images", [])
        sizes_data = validated_data.pop("sizes", [])
        colors_data = validated_data.pop("colors", [])
        frame_types_data = validated_data.pop("frame_types", [])

        product_type = None
        if not product_type_data:
            product_type = self.default_type
        else:
            try:
                product_type = ProductType.objects.get(id=product_type_data.get("id"))
            except ProductType.DoesNotExist:
                raise serializers.ValidationError(
                    "Product type does not exist", code=status.HTTP_400_BAD_REQUEST
                )

        grade = None
        if not grade_data:
            grade = self.default_grade
        else:
            try:
                grade = ProductGrade.objects.get(id=grade_data.get("id"))
            except ProductGrade.DoesNotExist:
                raise serializers.ValidationError(
                    "Product grade does not exist", code=status.HTTP_400_BAD_REQUEST
                )
        with transaction.atomic():
            request = self.context.get("request")
            user = request.user if request else None
            instance.name = validated_data.get("name", instance.name)
            instance.grade = grade or instance.grade
            instance.product_type = product_type or instance.product_type

            thought_themes = []
            if not themes_data:
                thought_themes.append(self.default_theme)
            else:
                try:
                    thought_themes = [
                        ThoughtTheme.objects.get(id=theme_data.get("id"))
                        for theme_data in themes_data
                    ]
                except ThoughtTheme.DoesNotExist:
                    raise serializers.ValidationError(
                        "A theme key does not exist", code=status.HTTP_400_BAD_REQUEST
                    )

            instance.themes.set(thought_themes)

            sizes = []
            if sizes_data:
                try:
                    sizes = [
                        Dimension.objects.get(id=size_data.get("id"))
                        for size_data in sizes_data
                    ]
                except Dimension.DoesNotExist:
                    raise serializers.ValidationError(
                        "A selected dimension does not exist",
                        code=status.HTTP_400_BAD_REQUEST,
                    )
            instance.sizes.set(sizes)

            colors = []
            if colors_data:
                try:
                    colors = [
                        Color.objects.get(id=color_data.get("id"))
                        for color_data in colors_data
                    ]
                except Color.DoesNotExist:
                    raise serializers.ValidationError(
                        "A selected color does not exist",
                        code=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                colors.append(self.default_color)

            instance.colors.set(colors)

            frame_types = []
            if frame_types_data:
                try:
                    frame_types = [
                        FrameType.objects.get(id=frame_type_data.get("id"))
                        for frame_type_data in frame_types_data
                    ]
                except FrameType.DoesNotExist:
                    raise serializers.ValidationError(
                        "A selected frame type does not exist",
                        code=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                frame_types.append(self.default_frame_type)
            instance.frame_types.set(frame_types)

            ProductImage.objects.bulk_create(
                [
                    ProductImage(product=instance, **image_data)
                    for image_data in images_data
                ]
            )
            instance.description = validated_data.get("description", "")
            instance.added_by = user
            instance.save()
            return instance


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ["id", "name"]


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = [
            "product",
            "qty",
            "tax",
            "discount",
            "promo_code",
            "product_cost",
            "total_cost",
        ]
        read_only_fields = ["id", "item_cost", "discount"]


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
            # "order_date",
            # "first_name",
            # "last_name",
            "status",
            "total_items_count",
            "total_items_cost",
        ]


class PromoCodeSerializer(serializers.ModelSerializer):
    code = serializers.CharField(allow_blank=True)

    class Meta:
        model = PromoCode
        fields = ["code", "value", "value_percentage"]
        read_only_fields = ["value", "value_percentage"]

    def validate(self, data: dict):
        promo_code_data: dict = data.get("promo_code", None)
        if promo_code_data and promo_code_data.get("code"):
            return data
        else:
            data.pop("promo_code", None)
            return data


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItems
        fields = [
            "id",
            "qty",
            "promo_code",
        ]


class ShippingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingInfo
        fields = ["shipping_address", "shipping_cost", "delivery_period"]
        read_only_fields = ["delivery_period", "shipping_cost"]


class PaymentInfoSerializer(serializers.ModelSerializer):
    payment_method = serializers.StringRelatedField()

    class Meta:
        model = PaymentInfo
        fields = ["payment_method", "amount_paid", "transaction_id", "payment_date"]


class OrderSerializer(serializers.ModelSerializer):
    promo_code = PromoCodeSerializer()
    items = OrderItemSerializer(many=True)
    status = OrderStatusSerializer(read_only=True)
    payment_status = serializers.StringRelatedField(read_only=True)
    shipping_info = ShippingInfoSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "items",
            "order_date",
            "status",
            "tax",
            "promo_code",
            "total_items_count",
            "shipping_cost",
            "total_items_cost",
            "total_order_cost",
            "payment_status",
            "shipping_info",
            "added_by",
            "first_name",
            "last_name",
            "email",
        ]
        read_only_fields = [
            "id",
            "order_number",
            "tax",
            "total_items_count",
            "total_items_cost",
            "shipping_cost",
            "total_order_cost",
            "payment_status",
            "added_by",
        ]

    def validate(self, data: dict):
        """
        this method validates whether user information
        has been included in the order details
        """
        print(f"data: {data}")
        self.user = self.context["request"].user if "request" in self.context else None
        if not self.user or self.user.is_anonymous:
            if not all(
                [
                    data.get("first_name", ""),
                    data.get("last_name", ""),
                    data.get("email", ""),
                ]
            ):
                raise exceptions.ValidationError(
                    "Sign in or fill in the necessary details",
                    # "An error has occured",
                    code=status.HTTP_400_BAD_REQUEST,
                )
        return data

    def create(self, validated_data: dict) -> dict:
        promo_code_data = validated_data.pop("promo_code", "")
        order_items_data = validated_data.pop("items", [])
        shipping_info_data = validated_data.pop("shipping_info", {})

        if not order_items_data:
            raise serializers.ValidationError(
                "No items have been selected", code=status.HTTP_400_BAD_REQUEST
            )
        try:
            with transaction.atomic():
                # create order object
                code = promo_code_data.get("code")
                promo_code = PromoCode.objects.get(code=code) if code else None
                # get default payment status
                payment_status = default_payment_status()
                shipping_cost = generate_shipping_cost()
                total_items_count = len(order_items_data)
                order = Order.objects.create(
                    promo_code=promo_code,
                    payment_status=payment_status,
                    shipping_cost=shipping_cost,
                    total_items_count=total_items_count,
                    **validated_data,
                )
                # create related shipping information
                ShippingInfo.objects.create(
                    # order=order, shipping_country=None, **shipping_info_data
                    order=order,
                    **shipping_info_data,
                )

                # creating associated order items
                order_items = []
                total_items_cost = 0
                total_order_cost = 0
                # print(f"order items: {order_items_data}")
                for order_item_data in order_items_data:
                    item_id = order_item_data.pop("id", "")
                    if item_id:
                        product = Product.objects.get(id=item_id)
                        item_discount = product.discount
                        qty = order_item_data.get("qty")
                        product_order_cost = float(qty * product.unit_price)
                        total_items_cost += product_order_cost
                        item_taxes = generate_order_taxes(product_order_cost)
                        total_item_tax = float(sum(item_taxes.values()))
                        total_cost = (
                            product_order_cost + total_item_tax - float(item_discount)
                        )
                        print(f"item_tax: {total_item_tax}")
                        OrderItems.objects.create(
                            order=order,
                            product=product,
                            qty=qty,
                            tax=total_item_tax,
                            discount=item_discount,
                            promo_code=promo_code,
                            product_order_cost=product_order_cost,
                            total_cost=total_cost,
                        )
                order.total_items_cost = total_items_cost
                order_tax = float(sum(generate_order_taxes(total_items_cost).values()))
                promo_code_value = float(promo_code.value) if promo_code else 0.00
                total_order_cost = total_items_cost + order_tax - promo_code_value
                print(f"order.total_items_cost: {order.total_items_cost}")
                order.total_order_cost = total_order_cost
                order.save()
            return order
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to create order {e}", code=status.HTTP_400_BAD_REQUEST
            )

    def update(self, instance, validated_data):
        promo_code_data = validated_data.pop("promo_code", "")
        order_items_data = validated_data.pop("items", [])
        shipping_info_data = validated_data.pop("shipping_info", {})

        if not order_items_data:
            raise serializers.ValidationError(
                "No items have been selected", code=status.HTTP_400_BAD_REQUEST
            )
        try:
            with transaction.atomic():
                # create order object
                order = Order.objects.create(promo_code=promo_code, **validated_data)
                # create related shipping information
                ShippingInfo.objects.create(
                    order=order, shipping_country=None, **shipping_info_data
                )
                # creating associated order items
                order_items = []
                for order_item_data in order_items_data:
                    item_id = order_item_data.pop("product", "")
                    if item_id:
                        product = Product.objects.get(id=item_id)
                        item_discount = product.discount
                        qty = order_item_data.get("qty")
                        product_cost = qty * product.unit_price
                        item_tax = generate_order_taxes(product_cost)
                        # get applied promo code details
                        promo_code = PromoCode.objects.get(code=promo_code_data)
                        promo_code_value = promo_code.value
                        total_cost = (
                            product_cost + item_tax - promo_code_value - item_discount
                        )
                        OrderItems.objects.create(
                            order=order,
                            product=product,
                            qty=qty,
                            tax=item_tax,
                            discount=item_discount,
                            promo_code=promo_code,
                            product_cost=product_cost,
                            total_cost=total_cost,
                        )
            return order
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to create order {e}", code=status.HTTP_400_BAD_REQUEST
            )


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
        self.user = self.context["request"].user if "request" in self.context else None
        if not self.user or self.user.is_anonymous:
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
        # user = self.context["request"].user if "request" in self.context else None
        # order_id = uuid.uuid4()
        order_items = validated_data.pop("items", [])
        if not order_items:
            raise exceptions.ValidationError(
                "No product selected.", code=status.HTTP_400_BAD_REQUEST
            )

        # handling anonymous user case
        if not self.user or self.user.is_anonymous:
            print(UNREGISTERED_USER_EMAIL)
            user, _ = Colleague.objects.get_or_create(
                email=UNREGISTERED_USER_EMAIL,
                defaults={"first_name": "Anonymous", "last_name": "User"},
            )
        order = Order.objects.create(
            added_by=self.user, items_count=len(order_items), **validated_data
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
                item_tax = generate_order_taxes(item_cost, TAX_PERCENTAGE)
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
