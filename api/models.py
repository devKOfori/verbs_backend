import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django_countries.fields import CountryField
from helpers.validators import validate_shipping_cost_percentage
from helpers.defaults import (
    product_grade_default,
    product_type_default,
    ORDER_QTY_DEFAULT,
    PRODUCT_QTY_DEFAULT,
    ORDER_DISCOUNT_DEFAULT,
    RESET_PASSWORD_STATUS_DEFAULT,
    SHIPPING_COST_DEFAULT,
    get_default_order_status,
    order_payment_status_default,
    product_frame_type_default,
    product_color_default,
)
from helpers.storage_paths import product_image_storage_path
from helpers.generators import generate_order_number
from helpers.system_variables import (
    UNREGISTERED_USER_EMAIL,
    UNREGISTERED_USER_PASSWORD,
    PROMO_CODE_STATUS_CHOICES,
)

# Create your models here.


class ColleagueManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email is required to create an account")

        if email == UNREGISTERED_USER_EMAIL:
            password = UNREGISTERED_USER_PASSWORD

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Colleague(AbstractBaseUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, editable=False, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    country = CountryField(blank_label="(Select Country)", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)

    USERNAME_FIELD = "email"

    objects = ColleagueManager()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True

    class Meta:
        db_table = "colleague"
        verbose_name = "Colleague"
        verbose_name_plural = "Colleagues"


RESET_PASSWORD_STATUS_CHOICES = {
    ("new", "New"),
    ("used", "Used"),
    ("expired", "Expired"),
}


class ResetPassword(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    email = models.EmailField()
    token = models.CharField(unique=True, db_index=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=7,
        choices=RESET_PASSWORD_STATUS_CHOICES,
        default=RESET_PASSWORD_STATUS_DEFAULT,
    )

    def __str__(self) -> str:
        return f"{self.token}"

    class Meta:
        db_table = "resetpassword"


class ProductType(models.Model):
    # eg. frame, other merch
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name


class ProductGrade(models.Model):
    # eg. essential, classic, premium, signature
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "productgrade"


class ThoughtTheme(models.Model):
    # eg. self-discovery, etc.
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "thoughtheme"
        verbose_name = "Thought Theme"
        verbose_name_plural = "Thought Themes"


class Color(models.Model):
    # eg. black, etc.
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "color"
        verbose_name = "Color"
        verbose_name_plural = "Colors"


class FrameType(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "frametype"
        verbose_name = "Frame Type"
        verbose_name_plural = "Frame Types"


class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_DEFAULT,
        default=product_type_default,
        related_name="products",
    )
    grade = models.ForeignKey(
        ProductGrade,
        on_delete=models.SET_DEFAULT,
        default=product_grade_default,
        related_name="products",
    )
    themes = models.ManyToManyField(ThoughtTheme, related_name="products")
    sizes = models.ManyToManyField("Dimension")
    weight = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    colors = models.ManyToManyField(Color)
    frame_types = models.ManyToManyField(FrameType)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    qty = models.PositiveIntegerField(default=PRODUCT_QTY_DEFAULT)
    description = models.TextField(default="-")
    return_policy = models.TextField(blank=True, null=True)
    discount = models.DecimalField(max_digits=3, decimal_places=1, default=0.00)

    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "product"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-added_at"]


class Dimension(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    width = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    height = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"

    class Meta:
        db_table = "dimension"


class ProductImage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    added_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to=product_image_storage_path)
    description = models.TextField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )

    def __str__(self) -> str:
        return self.photo

    class Meta:
        db_table = "productimage"
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"


class ProductReview(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    added_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        Colleague, on_delete=models.CASCADE, related_name="submitted_reviews"
    )

    def __str__(self):
        return f"review-{self.id}"

    class Meta:
        db_table = "productreview"
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        ordering = ["-added_at"]


class PromoCode(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    code = models.CharField(max_length=255, unique=True, db_index=True)
    value = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    value_percentage = models.DecimalField(max_digits=3, decimal_places=1, default=0.00)
    status = models.CharField(
        max_length=7, choices=PROMO_CODE_STATUS_CHOICES, default="invalid"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.code

    class Meta:
        db_table = "promocode"
        verbose_name = "Promo Code"
        verbose_name_plural = "Promo Codes"


class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    order_number = models.CharField(
        max_length=255, unique=True, db_index=True, default=generate_order_number
    )
    products = models.ManyToManyField(Product, through="OrderItems")
    order_date = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        Colleague,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True,
    )
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    status = models.ForeignKey(
        "OrderStatus", on_delete=models.SET_DEFAULT, default=get_default_order_status
    )
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    discount = models.DecimalField(
        max_digits=3, decimal_places=1, default=ORDER_DISCOUNT_DEFAULT
    )
    promo_code = models.ForeignKey(
        PromoCode, on_delete=models.SET_NULL, null=True, blank=True
    )
    total_items_count = models.PositiveIntegerField(default=0)
    total_items_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2)
    total_order_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    payment_status = models.ForeignKey(
        "OrderPaymentStatus",
        on_delete=models.SET_DEFAULT,
        default=order_payment_status_default,
    )
    accumulate_payment = models.BooleanField(
        default=False
    )  # this field specifies whether colleague wants to pay for item in small amounts. item is released when payment is complete
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.order_number}"

    class Meta:
        db_table = "order"


class OrderItems(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="orders"
    )
    qty = models.PositiveIntegerField(default=ORDER_QTY_DEFAULT)
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True)
    product_order_cost = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00
    )
    total_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self) -> str:
        return self.product.name

    @property
    def calculate_ordered_product_price(self):
        """
        this method returns the cost of a single ordered item
        """
        ordered_product_price = (
            ((100 - (self.product.discount)) / 100) * self.product.unit_price
        ) * self.qty
        return ordered_product_price

    @property
    def calculate_ordered_product_total_cost(self):
        if not self.promo_code:
            return self.calculate_ordered_product_price
        return self.calculate_ordered_product_price - self.promo_code.value

    def get_total_cost(self):
        """
        this method returns the final cost of an ordered product
        """
        return

    class Meta:
        db_table = "orderitem"
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class OrderPaymentStatus(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        db_table = "orderpaymentstatus"
        verbose_name = "Order Payment Status"
        verbose_name_plural = "Order Payment Statuses"


class OrderStatus(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        db_table = "orderstatus"
        verbose_name = "Order Status"
        verbose_name_plural = "Order Statuses"


class ShippingInfo(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="shipping_info"
    )
    # shipping_country = CountryField()
    shipping_address = models.TextField(blank=True, null=True)
    shipping_cost = models.DecimalField(
        max_digits=4, decimal_places=2, default=SHIPPING_COST_DEFAULT
    )
    delivery_period = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return self.shipping_address

    class Meta:
        db_table = "shippinginfo"
        verbose_name = "Shipping Info"
        verbose_name_plural = "Shipping Infos"


class PaymentMethod(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class PaymentInfo(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True
    )
    transaction_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self) -> str:
        return self.transaction_id

    class Meta:
        db_table = "paymentinfo"
        verbose_name = "Payment Info"
        verbose_name_plural = "Payment Infos"
