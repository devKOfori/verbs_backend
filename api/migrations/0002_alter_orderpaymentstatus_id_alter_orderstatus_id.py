# Generated by Django 5.1.2 on 2024-11-07 15:31

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
            field=models.UUIDField(default=uuid.UUID('9dcaebc5-35d7-46f2-b5a7-04eb48949acf'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='id',
            field=models.UUIDField(default=uuid.UUID('27bfcaca-3c51-4e96-88b6-7c2597e5fdee'), primary_key=True, serialize=False),
        ),
    ]
