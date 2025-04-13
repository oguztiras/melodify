# Generated by Django 5.1.5 on 2025-03-14 20:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunementor', '0002_alter_user_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstructorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True)),
                ('city', models.CharField(choices=[('berlin', 'Berlin'), ('munich', 'Munich'), ('hamburg', 'Hamburg')], default='berlin', max_length=32)),
                ('level', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate')], default='intermediate', max_length=32)),
                ('instructor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='instructor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=500)),
                ('reciever', models.ManyToManyField(related_name='recieved_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ManyToManyField(related_name='sended_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
