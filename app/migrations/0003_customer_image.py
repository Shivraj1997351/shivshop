# Generated by Django 3.2.6 on 2021-09-08 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_customer_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='image',
            field=models.ImageField(blank=True, upload_to='media/profileimg'),
        ),
    ]
