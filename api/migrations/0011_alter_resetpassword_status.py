# Generated by Django 5.1.2 on 2024-12-03 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resetpassword',
            name='status',
            field=models.CharField(choices=[('used', 'Used'), ('expired', 'Expired'), ('new', 'New')], default='new', max_length=7),
        ),
    ]