# Generated by Django 4.2.16 on 2025-04-09 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunementor', '0018_remove_message_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
