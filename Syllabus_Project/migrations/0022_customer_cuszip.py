# Generated by Django 4.2.7 on 2023-11-20 03:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Syllabus_Project", "0021_customer_cuscity"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="cusZip",
            field=models.IntegerField(blank=True, max_length=6, null=True),
        ),
    ]