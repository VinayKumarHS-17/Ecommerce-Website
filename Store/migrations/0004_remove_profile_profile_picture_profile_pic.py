# Generated by Django 5.1.6 on 2025-03-25 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Store", "0003_profile_phone"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="profile_picture",
        ),
        migrations.AddField(
            model_name="profile",
            name="pic",
            field=models.ImageField(
                blank=True, default="default_profile.png", upload_to="profile_pics/"
            ),
        ),
    ]
