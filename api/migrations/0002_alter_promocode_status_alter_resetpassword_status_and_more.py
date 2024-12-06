# Generated by Django 5.1.2 on 2024-11-22 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
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
            field=models.CharField(choices=[('used', 'Used'), ('expired', 'Expired'), ('new', 'New')], default='new', max_length=7),
        ),
        migrations.AlterField(
            model_name='shippinginfo',
            name='shipping_cost',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4),
        ),
    ]