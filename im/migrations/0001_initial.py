# Generated by Django 5.1.3 on 2024-11-23 16:07

import django.db.models.deletion
from django.db import migrations, models


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
                ("sku", models.CharField(max_length=100, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("weight", models.FloatField(help_text="Weight of the product in kg")),
                (
                    "volume",
                    models.FloatField(help_text="Volume of the product in cubic units"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Store",
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
                ("name", models.CharField(max_length=200, unique=True)),
                (
                    "location",
                    models.CharField(
                        blank=True,
                        help_text="Store location",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "capacity",
                    models.FloatField(
                        help_text="Maximum storage capacity in cubic units"
                    ),
                ),
                (
                    "lead_time_mean",
                    models.FloatField(
                        help_text="Mean lead time for deliveries in days"
                    ),
                ),
                (
                    "lead_time_std",
                    models.FloatField(
                        help_text="Standard deviation of lead time in days"
                    ),
                ),
                ("container_cost", models.FloatField(help_text="Cost per container")),
                (
                    "container_capacity",
                    models.FloatField(
                        help_text="Capacity of one container in cubic units"
                    ),
                ),
                (
                    "ordering_cost_kg",
                    models.FloatField(help_text="Cost per kg for ordering products"),
                ),
                (
                    "holding_cost_kg",
                    models.FloatField(help_text="Cost per kg for holding inventory"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductGlobalData",
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
                    "total_inventory",
                    models.PositiveIntegerField(
                        default=0, help_text="Total inventory across all stores"
                    ),
                ),
                (
                    "total_sales",
                    models.PositiveIntegerField(
                        default=0, help_text="Total sales across all stores"
                    ),
                ),
                (
                    "average_demand",
                    models.FloatField(
                        default=0,
                        help_text="Combined average daily demand across all stores",
                    ),
                ),
                (
                    "demand_std",
                    models.FloatField(
                        default=0,
                        help_text="Combined demand standard deviation across all stores",
                    ),
                ),
                (
                    "last_calculated",
                    models.DateTimeField(
                        auto_now=True, help_text="Last time metrics were calculated"
                    ),
                ),
                (
                    "product",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="global_data",
                        to="im.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Sale",
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
                    "quantity",
                    models.PositiveIntegerField(
                        help_text="Quantity of the product sold"
                    ),
                ),
                ("sale_date", models.DateField(help_text="Date of the sale")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sales",
                        to="im.product",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sales",
                        to="im.store",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductStoreData",
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
                    "inventory_level",
                    models.PositiveIntegerField(
                        default=0, help_text="Current inventory level in this store"
                    ),
                ),
                (
                    "total_sales",
                    models.PositiveIntegerField(
                        default=0, help_text="Total sales quantity in this store"
                    ),
                ),
                (
                    "average_demand",
                    models.FloatField(
                        default=0, help_text="Average daily demand in this store"
                    ),
                ),
                (
                    "demand_std",
                    models.FloatField(
                        default=0, help_text="Demand standard deviation in this store"
                    ),
                ),
                (
                    "shortage_cost_item",
                    models.FloatField(
                        help_text="Cost per item for shortages in this store"
                    ),
                ),
                (
                    "lost_demand_cost_item",
                    models.FloatField(
                        help_text="Cost per item for lost demand in this store"
                    ),
                ),
                (
                    "last_calculated",
                    models.DateTimeField(
                        auto_now=True, help_text="Last time metrics were calculated"
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="store_data",
                        to="im.product",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_data",
                        to="im.store",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductOrder",
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
                    "quantity",
                    models.PositiveIntegerField(
                        help_text="Quantity of the product ordered"
                    ),
                ),
                ("order_date", models.DateField(help_text="Date the order was placed")),
                (
                    "expected_delivery_date",
                    models.DateField(help_text="Expected delivery date for the order"),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to="im.product",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to="im.store",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Demand",
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
                    "quantity",
                    models.PositiveIntegerField(
                        help_text="Quantity of the product demand"
                    ),
                ),
                ("demand_date", models.DateField(help_text="Date of the demand")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="demand",
                        to="im.product",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="demand",
                        to="im.store",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Backlog",
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
                    "quantity",
                    models.PositiveIntegerField(
                        help_text="Quantity of the product backlog"
                    ),
                ),
                ("backlog_date", models.DateField(help_text="Date of the backlog")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="backlog",
                        to="im.product",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="backlog",
                        to="im.store",
                    ),
                ),
            ],
        ),
    ]
