# Generated by Django 4.2.5 on 2023-10-18 05:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_product_visible"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="main_image",
        ),
    ]