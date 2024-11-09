import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django_countries.fields import CountryField
from helpers.validators import validate_shipping_cost_percentage
from helpers.defaults import (
    product_grade_default,
    product_type_default,
    ORDER_QTY_DEFAULT,
    order_status_default,
    order_payment_status_default,
)
from helpers.storage_paths import product_image_storage_path
from helpers.generators import generate_order_number
from helpers.system_variables import UNREGISTERED_USER_EMAIL, UNREGISTERED_USER_PASSWORD

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


class ProductType(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name


class ProductGrade(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name


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
    unit_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    availability = models.BooleanField(default=True)
    description = models.TextField(default="-")
    specifications = models.TextField(blank=True, null=True)
    shipping_cost = models.PositiveIntegerField(default=0)
    shipping_cost_percentage = models.PositiveIntegerField(
        validators=[validate_shipping_cost_percentage], default=0
    )
    width = models.PositiveIntegerField(default=1)
    height = models.PositiveIntegerField(default=1)
    weight = models.PositiveIntegerField(default=0)
    return_policy = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "product"
        verbose_name = "Product"
        verbose_name_plural = "Products"


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


class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    order_number = models.CharField(
        max_length=255, unique=True, db_index=True, default=generate_order_number
    )
    order_date = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        Colleague,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True,
    )
    products = models.ManyToManyField(Product, through="OrderItems")
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    shipping_country = CountryField()
    shipping_address = models.TextField(blank=True, null=True)
    status = models.ForeignKey(
        "OrderStatus", on_delete=models.SET_DEFAULT, default=order_status_default
    )
    items_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    items_count = models.PositiveIntegerField(default=0)
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    payment_status = models.ForeignKey(
        "OrderPaymentStatus",
        on_delete=models.SET_DEFAULT,
        default=order_payment_status_default,
    )

    def __str__(self) -> str:
        return f"{self.order_number}"

    class Meta:
        db_table = "order"


class OrderItems(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=ORDER_QTY_DEFAULT)
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self) -> str:
        return f"ORDER - {self.id} --- [{self.product} - {self.qty}]"

    class Meta:
        db_table = "orderitem"
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class OrderPaymentStatus(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True)
    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        db_table = "orderpaymentstatus"
        verbose_name = "Order Payment Status"
        verbose_name_plural = "Order Payment Statuses"


class OrderStatus(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True)
    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        db_table = "orderstatus"
        verbose_name = "Order Status"
        verbose_name_plural = "Order Statuses"
