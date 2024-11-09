# Generated by Django 5.1.2 on 2024-11-07 14:23

import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import helpers.defaults
import helpers.generators
import helpers.storage_paths
import helpers.validators
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Colleague',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('full_name', models.CharField(editable=False, max_length=255, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Colleague',
                'verbose_name_plural': 'Colleagues',
                'db_table': 'colleague',
            },
        ),
        migrations.CreateModel(
            name='OrderPaymentStatus',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('b3611ed6-ee16-47be-a5fa-bde8de8e0c19'), primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Order Payment Status',
                'verbose_name_plural': 'Order Payment Statuses',
                'db_table': 'orderpaymentstatus',
            },
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('0664e66d-f87e-4763-bc75-8f6cf0cce502'), primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Order Status',
                'verbose_name_plural': 'Order Statuses',
                'db_table': 'orderstatus',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('unit_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('availability', models.BooleanField(default=True)),
                ('description', models.TextField(default='-')),
                ('specifications', models.TextField(blank=True, null=True)),
                ('shipping_cost', models.PositiveIntegerField(default=0)),
                ('shipping_cost_percentage', models.PositiveIntegerField(default=0, validators=[helpers.validators.validate_shipping_cost_percentage])),
                ('width', models.PositiveIntegerField(default=1)),
                ('height', models.PositiveIntegerField(default=1)),
                ('weight', models.PositiveIntegerField(default=0)),
                ('return_policy', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'db_table': 'product',
            },
        ),
        migrations.CreateModel(
            name='ProductGrade',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('order_number', models.CharField(db_index=True, default=helpers.generators.generate_order_number, max_length=255, unique=True)),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('shipping_country', django_countries.fields.CountryField(max_length=2)),
                ('shipping_address', models.TextField(blank=True, null=True)),
                ('items_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('items_count', models.PositiveIntegerField(default=0)),
                ('tax', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
                ('payment_status', models.ForeignKey(default=helpers.defaults.order_payment_status_default, on_delete=django.db.models.deletion.SET_DEFAULT, to='api.orderpaymentstatus')),
                ('status', models.ForeignKey(default=helpers.defaults.order_status_default, on_delete=django.db.models.deletion.SET_DEFAULT, to='api.orderstatus')),
            ],
            options={
                'db_table': 'order',
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('qty', models.PositiveIntegerField(default=1)),
                ('tax', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='api.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
            options={
                'verbose_name': 'Order Item',
                'verbose_name_plural': 'Order Items',
                'db_table': 'orderitem',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(through='api.OrderItems', to='api.product'),
        ),
        migrations.AddField(
            model_name='product',
            name='grade',
            field=models.ForeignKey(default=helpers.defaults.product_grade_default, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='products', to='api.productgrade'),
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ImageField(upload_to=helpers.storage_paths.product_image_storage_path)),
                ('description', models.TextField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='api.product')),
            ],
            options={
                'verbose_name': 'Product Image',
                'verbose_name_plural': 'Product Images',
                'db_table': 'productimage',
            },
        ),
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='api.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Product Review',
                'verbose_name_plural': 'Product Reviews',
                'db_table': 'productreview',
                'ordering': ['-added_at'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(default=helpers.defaults.product_type_default, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='products', to='api.producttype'),
        ),
    ]
