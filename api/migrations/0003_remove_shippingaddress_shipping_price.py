# Generated by Django 4.2.5 on 2023-11-12 03:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_remove_orderitem_quantity_orderitem_colors_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="shippingaddress",
            name="shipping_price",
        ),
    ]