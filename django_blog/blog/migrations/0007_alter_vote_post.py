# Generated by Django 3.2.23 on 2023-12-17 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_vote_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vote', to='blog.blog'),
        ),
    ]
