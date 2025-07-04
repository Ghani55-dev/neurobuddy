# Generated by Django 5.2.3 on 2025-06-23 16:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WearableData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heart_rate', models.IntegerField(blank=True, null=True)),
                ('steps', models.IntegerField(blank=True, null=True)),
                ('sleep_hours', models.FloatField(blank=True, null=True)),
                ('source', models.CharField(default='fitbit', max_length=50)),
                ('collected_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
