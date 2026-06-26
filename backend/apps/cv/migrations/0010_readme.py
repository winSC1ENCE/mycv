# Generated for the per-application README feature.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cv", "0009_person_active_funny_theme"),
    ]

    operations = [
        migrations.CreateModel(
            name="Readme",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("order", models.PositiveIntegerField(db_index=True, default=0)),
                ("is_published", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(help_text="Application/company label.", max_length=160)),
                ("content", models.TextField(blank=True)),
                ("content_de", models.TextField(blank=True)),
                ("version", models.CharField(default="v1.0.0", max_length=40)),
                (
                    "access_key",
                    models.ForeignKey(
                        blank=True,
                        help_text="Source for the auto-filled access URL and expiry date.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="readmes",
                        to="cv.accesskey",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="readmes",
                        to="cv.person",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "id"],
                "abstract": False,
            },
        ),
    ]
