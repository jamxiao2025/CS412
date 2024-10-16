# Generated by Django 4.2.16 on 2024-10-15 19:45

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("mini_fb", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatusMessage",
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
                    "timestamp",
                    models.DateTimeField(
                        default=datetime.datetime(
                            2024,
                            10,
                            15,
                            19,
                            45,
                            33,
                            513182,
                            tzinfo=datetime.timezone.utc,
                        )
                    ),
                ),
                ("message", models.TextField()),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_messages",
                        to="mini_fb.profile",
                    ),
                ),
            ],
        ),
    ]
