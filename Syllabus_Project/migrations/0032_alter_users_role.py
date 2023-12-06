# Generated by Django 4.2.7 on 2023-12-02 09:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "Syllabus_Project",
            "0031_remove_customer_cususer_customer_cuspassword_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="users",
            name="role",
            field=models.CharField(
                choices=[
                    ("Admin", "Admin"),
                    ("SalesRep", "SalesRep"),
                    ("SalesAdmin", "SalesAdmin"),
                    ("HR", "HR"),
                    ("Operations", "Operations"),
                    ("cus", "cus"),
                ],
                max_length=20,
            ),
        ),
    ]