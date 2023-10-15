# Generated by Django 4.2.5 on 2023-10-15 04:33

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("price", models.DecimalField(decimal_places=2, max_digits=7)),
                (
                    "main_image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=api.models.product_image_upload_path,
                    ),
                ),
                (
                    "model_3d",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=api.models.product_model_upload_path,
                    ),
                ),
                ("customization_data", models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(upload_to=api.models.product_image_upload_path),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="api.product",
                    ),
                ),
            ],
        ),
    ]
