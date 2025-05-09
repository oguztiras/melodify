# Generated by Django 5.1.5 on 2025-04-04 20:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunementor', '0009_instrument_instructorprofile_instruments'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstructorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_datetime', models.DateTimeField()),
                ('duration', models.DurationField(help_text='Lesson duration (e.g., 1:00:00 for one hour)')),
                ('state', models.CharField(choices=[('scheduled', 'Scheduled'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='scheduled', max_length=10)),
                ('cancellation_reason', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons_given', to=settings.AUTH_USER_MODEL)),
                ('instrument', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lessons', to='tunementor.instrument')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons_taken', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
