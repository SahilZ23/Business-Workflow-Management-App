# Generated by Django 4.2.7 on 2023-11-20 04:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Syllabus_Project", "0025_alter_orders_orderamount"),
    ]

    operations = [
        migrations.AddField(
            model_name="personalinfo",
            name="city",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name="personalinfo",
            name="state",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="personalinfo",
            name="zip",
            field=models.IntegerField(blank=True, max_length=6, null=True),
        ),
    ]
