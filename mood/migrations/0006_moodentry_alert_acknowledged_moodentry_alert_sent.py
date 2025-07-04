# Generated by Django 5.2.3 on 2025-06-23 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mood', '0005_alter_moodentry_sentiment'),
    ]

    operations = [
        migrations.AddField(
            model_name='moodentry',
            name='alert_acknowledged',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='moodentry',
            name='alert_sent',
            field=models.BooleanField(default=False),
        ),
    ]
