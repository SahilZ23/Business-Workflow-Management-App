# Generated by Django 4.2.7 on 2023-11-20 03:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "Syllabus_Project",
            "0020_employee_users_hours_users_pay_rate_delete_employees_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="cusCity",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
