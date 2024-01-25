# Generated by Django 3.2.23 on 2023-12-22 07:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0008_alter_vote_post"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vote",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vote",
                to="blog.blog",
            ),
        ),
    ]
