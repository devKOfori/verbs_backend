# Generated by Django 5.1.2 on 2024-11-17 09:16

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderpaymentstatus',
            name='id',
            field=models.UUIDField(default=uuid.UUID('362124d9-0b72-458b-ad76-25b0845da3af'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='id',
            field=models.UUIDField(default=uuid.UUID('1038e3dd-ad1e-42f4-98ad-ca91bd27270f'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='status',
            field=models.CharField(choices=[('valid', 'Valid'), ('invalid', 'Invalid')], default='invalid', max_length=7),
        ),
        migrations.AlterField(
            model_name='resetpassword',
            name='status',
            field=models.CharField(choices=[('used', 'Used'), ('new', 'New'), ('expired', 'Expired')], default='new', max_length=7),
        ),
    ]
