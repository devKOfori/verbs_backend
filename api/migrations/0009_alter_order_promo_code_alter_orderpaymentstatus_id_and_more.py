# Generated by Django 5.1.2 on 2024-11-14 09:56

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_order_promo_code_alter_orderpaymentstatus_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='promo_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.promocode'),
        ),
        migrations.AlterField(
            model_name='orderpaymentstatus',
            name='id',
            field=models.UUIDField(default=uuid.UUID('f9db66e4-728f-4cf9-97c8-8f24e6727bbb'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='id',
            field=models.UUIDField(default=uuid.UUID('22a8189a-d49b-44fc-a7a7-d44ceec3aeb9'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='resetpassword',
            name='status',
            field=models.CharField(choices=[('new', 'New'), ('used', 'Used'), ('expired', 'Expired')], default='new', max_length=7),
        ),
    ]
