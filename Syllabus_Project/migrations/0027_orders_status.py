# Generated by Django 4.2.7 on 2023-11-24 17:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Syllabus_Project", "0026_personalinfo_city_personalinfo_state_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="orders",
            name="status",
            field=models.CharField(default="Placed", max_length=10),
        ),
    ]
