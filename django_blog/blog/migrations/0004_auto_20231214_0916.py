# Generated by Django 3.2.23 on 2023-12-14 09:16

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("blog", "0003_vote"),
    ]

    operations = [
        migrations.RenameField(
            model_name="vote",
            old_name="author",
            new_name="user",
        ),
        migrations.AlterUniqueTogether(
            name="vote",
            unique_together={("post", "user")},
        ),
    ]
