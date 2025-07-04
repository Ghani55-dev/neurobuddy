# Generated by Django 5.2.3 on 2025-06-22 11:21

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mood', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MoodSuggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('quote', '💬 Motivational Quote'), ('video', '🎬 Calming Video'), ('tip', '💡 Wellness Tip'), ('activity', '🏃 Mindful Activity'), ('prompt', '✍️ Reflection Prompt')], max_length=20)),
                ('title', models.CharField(default='General Suggestion', max_length=100)),
                ('content', models.TextField()),
                ('video_url', models.URLField(blank=True, null=True)),
                ('duration_minutes', models.PositiveSmallIntegerField(blank=True, help_text='Duration in minutes (for activities/videos)', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['category', 'title'],
            },
        ),
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100)),
                ('mood', models.CharField(choices=[('Happy', '😊 Happy'), ('Sad', '😢 Sad'), ('Anxious', '😨 Anxious'), ('Angry', '😠 Angry'), ('Excited', '🤩 Excited'), ('Tired', '😴 Tired'), ('Neutral', '😐 Neutral')], default='Neutral', max_length=20)),
                ('content', models.TextField()),
                ('ai_insight', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags', max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='journal_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Journal Entries',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MoodEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mood_score', models.IntegerField(choices=[(1, '😢 Very Low'), (2, '😟 Low'), (3, '😐 Neutral'), (4, '😊 Good'), (5, '😁 Very Good')])),
                ('note', models.TextField(blank=True, null=True)),
                ('journal', models.TextField(blank=True, null=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('sentiment', models.CharField(blank=True, choices=[('Positive', 'Positive'), ('Negative', 'Negative'), ('Neutral', 'Neutral')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mood_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Mood Entries',
                'ordering': ['-date', '-created_at'],
                'unique_together': {('user', 'date')},
            },
        ),
    ]
