# Generated by Django 4.2.2 on 2023-10-31 21:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Syllabus_Project", "0004_alter_users_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="items",
            name="ItemPrice",
            field=models.IntegerField(default=0),
        ),
    ]