# Generated by Django 5.2 on 2025-04-28 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
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
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=100)),
                ("publisher", models.CharField(max_length=100)),
                ("price", models.IntegerField()),
                ("pubdate", models.DateField()),
                ("description", models.TextField()),
                ("image", models.CharField(max_length=255)),
            ],
        ),
    ]
