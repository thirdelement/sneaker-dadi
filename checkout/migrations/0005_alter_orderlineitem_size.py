# Generated by Django 3.2.4 on 2021-09-06 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0004_order_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlineitem',
            name='size',
            field=models.CharField(blank=True, max_length=4),
        ),
    ]
