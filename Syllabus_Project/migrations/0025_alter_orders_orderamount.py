# Generated by Django 4.2.7 on 2023-11-20 03:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Syllabus_Project", "0024_alter_items_itemprice"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orders",
            name="orderAmount",
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
