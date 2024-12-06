# Generated by Django 5.1.2 on 2024-12-06 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_confirmationcodestatus_colleague_confirmation_code_and_more'),
    ]

    operations = [
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