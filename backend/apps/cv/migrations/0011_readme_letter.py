# Generated for the per-application motivation letter feature.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cv", "0010_readme"),
    ]

    operations = [
        migrations.AddField(
            model_name="readme",
            name="letter_content",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="readme",
            name="letter_content_de",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="readme",
            name="letter_reference",
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
