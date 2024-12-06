# Generated by Django 5.1.2 on 2024-12-03 16:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_colleague_is_employee_alter_promocode_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='promocode',
            name='status',
            field=models.CharField(choices=[('invalid', 'Invalid'), ('valid', 'Valid')], default='invalid', max_length=7),
        ),
        migrations.AlterField(
            model_name='resetpassword',
            name='status',
            field=models.CharField(choices=[('expired', 'Expired'), ('used', 'Used'), ('new', 'New')], default='new', max_length=7),
        ),
        migrations.AlterField(
            model_name='staff',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
