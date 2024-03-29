# Generated by Django 4.2.7 on 2023-12-14 23:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Syllabus_Project", "0034_remove_customer_cuspassword_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("due_date", models.DateField()),
                ("status", models.CharField(max_length=50)),
                ("description", models.TextField()),
            ],
        ),
    ]
