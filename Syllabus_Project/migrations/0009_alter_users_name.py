# Generated by Django 4.2.2 on 2023-10-31 22:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Syllabus_Project", "0008_alter_users_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="users",
            name="name",
            field=models.CharField(max_length=100),
        ),
    ]
