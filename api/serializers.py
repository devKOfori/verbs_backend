import datetime
import pytz
from django.core.mail import EmailMessage
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
from helpers.system_variables import TAX_PERCENTAGE, UNREGISTERED_USER_EMAIL, TAXES
from helpers.generators import (
    generate_order_taxes,
    generate_reset_password_token,
    generate_shipping_cost,
    generate_order_number,
)
from helpers.defaults import (
    product_type_default,
    product_grade_default,
    product_color_default,
    default_payment_status,
    get_default_order_status,
    get_walk_in_colleague,
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
        self.default_frame_type, _ = frame_type = FrameType.objects.get_or_create(
            name="Default Type"
        )

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

            if sizes_data:
                sizes = [
                    Dimension.objects.get_or_create(
                        width=size_data["width"], height=size_data["height"]
                    )[0]
                    for size_data in sizes_data
                ]
                product.sizes.set(sizes)

            colors = []
            if colors_data:
                colors = [
                    Color.objects.get_or_create(**color_data)[0]
                    for color_data in colors_data
                ]
            else:
                colors.append(self.default_color)

            product.colors.set(colors)

            frame_types = []
            if frame_types_data:
                frame_types = [
                    FrameType.objects.get_or_create(**frame_type_data)[0]
                    for frame_type_data in frame_types_data
                ]
            else:
                frame_types.append(self.default_frame_type)
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
            instance.name = validated_data.get("name")
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

            if sizes_data:
                sizes = [
                    Dimension.objects.get_or_create(
                        width=size_data["width"], height=size_data["height"]
                    )[0]
                    for size_data in sizes_data
                ]
                instance.sizes.set(sizes)

            colors = []
            if colors_data:
                colors = [
                    Color.objects.get_or_create(**color_data)[0]
                    for color_data in colors_data
                ]
            else:
                colors.append(self.default_color)

            instance.colors.set(colors)

            frame_types = []
            if frame_types_data:
                frame_types = [
                    FrameType.objects.get_or_create(**frame_type_data)[0]
                    for frame_type_data in frame_types_data
                ]
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
    # promo_code = PromoCodeSerializer(required=False)
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
        ]

    def validate_promo_code(self, value):
        # print(value)
        # # Allow None or empty dictionaries for promo_code
        # if value is None or value.get("code", "") == "":
        #     return None  # Replace empty promo_code with None
        # return value
        raise serializers.ValidationError("invalide promo code")

    def validate(self, data: dict):
        """
        this method validates whether user information
        has been included in the order details
        """
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

    def create(self, validated_data: dict) -> dict:
        # print(validated_data)
        promo_code_data = validated_data.pop("promo_code", {})
        print(f"Promo code: {validated_data.get("promo_code")}")
        order_items_data = validated_data.pop("items", [])
        shipping_info_data = validated_data.pop("shipping_info", {})

        if not order_items_data:
            raise serializers.ValidationError(
                "No items have been selected", code=status.HTTP_400_BAD_REQUEST
            )
        try:
            with transaction.atomic():
                # create order object
                # try:
                #     code = promo_code_data.get("code")
                #     promo_code = PromoCode.objects.get(code=code) if promo_code_data else None
                # except PromoCode.DoesNotExist:
                #     raise serializers.ValidationError(
                #         "Invalid promo code", code=status.HTTP_400_BAD_REQUEST
                #     )
                # except KeyError:
                #     raise serializers.ValidationError("No promo code has been included")

                # get default payment status
                payment_status = default_payment_status()
                shipping_cost = generate_shipping_cost()
                total_items_count = len(order_items_data)
                order = Order.objects.create(
                    promo_code=None,
                    payment_status=payment_status,
                    shipping_cost=shipping_cost,
                    total_items_count=total_items_count,
                    **validated_data,
                )
                # create related shipping information
                ShippingInfo.objects.create(
                    order=order, shipping_country=None, **shipping_info_data
                )
                # creating associated order items
                order_items = []
                total_items_cost = 0
                total_order_cost = 0
                for order_item_data in order_items_data:
                    item_id = order_item_data.pop("id", "")
                    if item_id:
                        product = Product.objects.get(id=item_id)
                        item_discount = product.discount
                        qty = order_item_data.get("qty")
                        product_cost = qty * product.unit_price
                        total_items_cost += product_cost
                        item_tax = generate_tax(product_cost)
                        total_cost = product_cost + item_tax - item_discount
                        OrderItems.objects.create(
                            order=order,
                            product=product,
                            qty=qty,
                            tax=item_tax,
                            discount=item_discount,
                            # promo_code=promo_code,
                            product_cost=product_cost,
                            total_cost=total_cost,
                        )
                order.total_items_cost = total_items_cost
                order_tax = generate_tax(total_items_cost)
                # total_order_cost = total_items_cost + order_tax - promo_code.value
                total_order_cost = total_items_cost + order_tax
                order.total_order_cost = total_order_cost
                order.save()
            return order
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to create order {e}", code=status.HTTP_400_BAD_REQUEST
            )


class OrderSerializer(serializers.ModelSerializer):
    promo_code = PromoCodeSerializer()
    items = OrderItemSerializer(many=True)
    status = OrderStatusSerializer(read_only=True)
    payment_status = serializers.StringRelatedField(read_only=True)
    shipping_info = ShippingInfoSerializer()

    class Meta:
        model = Order

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
        ]

    def validate(self, data: dict):
        promo_code_data: dict = data.get("promo_code", None)
        if promo_code_data and promo_code_data.get("code"):
            return data
        else:
            data.pop("promo_code", None)
            return data

    def create(self, validated_data: dict):
        print(validated_data)
        shipping_cost = generate_shipping_cost()
        products_data = validated_data.pop("items", [])
        promo_code_data = validated_data.pop("promo_code", None)
        shipping_info_data = validated_data.pop("shipping_info", {})
        order_number = generate_order_number()
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")
        email = validated_data.get("email", "")
        walk_in_colleague = get_walk_in_colleague()
        if not products_data:
            raise serializers.ValidationError(
                "No items have been selected", code=status.HTTP_400_BAD_REQUEST
            )
        products: list = []
        ordered_products: list = []
        total_items_count = 0
        # ordered_products_cost: list = []
        for product_data in products_data:
            product_id, qty = product_data["id"], product_data["qty"]
            product = Product.objects.get(id=product_id)
            products.append(product)
            total_items_count += qty
            ordered_product = OrderItems(product=product, qty=qty)
            ordered_products.append(ordered_product)
        products_cost = sum(
            [
                ordered_product.calculate_ordered_product_price
                for ordered_product in ordered_products
            ]
        )
        taxes = generate_order_taxes(products_cost, TAXES)
        print(taxes)
        order_tax = sum(taxes.values())
        discount = 0.00
        promo_code = promo_code_data["code"] if promo_code_data else None
        added_by = self.context["request"].user if "request" in self.context else None
        print(f"self.context = {self.context["request"].user}")
        user_is_anonymous = added_by.is_anonymous
        if not all(
            [
                added_by,
                user_is_anonymous,
                validated_data.get("first_name"),
                validated_data.get("last_name"),
                validated_data.get("email"),
            ]
        ):
            raise serializers.ValidationError(
                "Sign in or fill in the necessary personal information"
            )
        if added_by and not user_is_anonymous:
            walk_in_colleague = added_by
            if not all([first_name, last_name, email]):
                first_name = added_by.first_name
                last_name = added_by.last_name
                email = added_by.email
        if not added_by or user_is_anonymous:
            added_by = get_walk_in_colleague()
        order_status = get_default_order_status()
        total_items_cost = (((100 - discount) / 100) * float(products_cost)) + order_tax
        payment_status = default_payment_status()
        shipping_cost = 0.00
        total_order_cost = sum([total_items_cost, order_tax])
        with transaction.atomic():
            order = Order.objects.create(
                order_number=order_number,
                order_date=validated_data.get(
                    "order_date", datetime.datetime.now(pytz.utc)
                ),
                added_by=walk_in_colleague,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=validated_data.get("phone_number", ""),
                status=order_status,
                tax=order_tax,
                discount=discount,
                promo_code=promo_code,
                total_items_count=total_items_count,
                total_items_cost=total_items_cost,
                payment_status=payment_status,
                shipping_cost=shipping_cost,
                total_order_cost=total_order_cost,
            )
            for ordered_product in ordered_products:
                ordered_product.order = order
                ordered_product.tax = 0
                ordered_product.discount = ordered_product.product.discount
                ordered_product.promo_code = None
                ordered_product.product_order_cost = (
                    ordered_product.product.unit_price * qty
                )
                ordered_product.total_cost = 0
                ordered_product.save()
        return order


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
