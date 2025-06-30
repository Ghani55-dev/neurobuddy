from django.contrib import admin
from .models import MoodEntry, MoodSuggestion

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'mood_score', 'sentiment', 'journal','date')
    list_filter = ('date', 'sentiment', 'mood_score')
    search_fields = ('user__username', 'note')



@admin.register(MoodSuggestion)
class MoodSuggestionAdmin(admin.ModelAdmin):
    list_display = ('category', 'video_url', 'content')
    list_filter = ('category', 'created_at')
    search_fields = ('category', 'content')