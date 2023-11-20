# Generated by Django 4.2.7 on 2023-11-20 01:24

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("Syllabus_Project", "0018_alter_employee_hours"),
    ]

    operations = [
        migrations.CreateModel(
            name="Employees",
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
                ("pay_rate", models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
        migrations.AddField(
            model_name="users",
            name="emp_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.DeleteModel(
            name="Employee",
        ),
        migrations.AddField(
            model_name="employees",
            name="emp",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="Syllabus_Project.users",
            ),
        ),
    ]
