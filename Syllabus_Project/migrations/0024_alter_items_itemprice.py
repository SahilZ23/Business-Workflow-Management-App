# Generated by Django 4.2.7 on 2023-11-20 03:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Syllabus_Project", "0023_customer_cusstate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="items",
            name="ItemPrice",
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
