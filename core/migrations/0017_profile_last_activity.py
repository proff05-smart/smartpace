# Generated by Django 5.2.3 on 2025-07-03 19:30

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_quizresult_date_taken_quizresult_time_used_seconds_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_activity',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
