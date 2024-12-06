# Generated by Django 5.1.2 on 2024-12-03 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_resetpassword_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='colleague',
            name='full_name',
        ),
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
    ]
