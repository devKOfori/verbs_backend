# Generated by Django 5.1.2 on 2024-11-13 11:06

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_orderitems_product_alter_orderpaymentstatus_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitems',
            old_name='item_cost',
            new_name='product_cost',
        ),
        migrations.AddField(
            model_name='orderitems',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
        migrations.AddField(
            model_name='product',
            name='discount',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=3),
        ),
        migrations.AlterField(
            model_name='orderpaymentstatus',
            name='id',
            field=models.UUIDField(default=uuid.UUID('d1a4b803-4cb6-4575-a020-947a69c0b075'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='id',
            field=models.UUIDField(default=uuid.UUID('3e9900f6-9073-449d-9a8a-9fd8384b4e35'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='status',
            field=models.CharField(choices=[('valid', 'Valid'), ('invalid', 'Invalid')], default='invalid', max_length=7),
        ),
        migrations.AlterField(
            model_name='resetpassword',
            name='status',
            field=models.CharField(choices=[('expired', 'Expired'), ('new', 'New'), ('used', 'Used')], default='new', max_length=7),
        ),
        migrations.AlterField(
            model_name='shippinginfo',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_info', to='api.order'),
        ),
    ]
