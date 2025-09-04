from django.contrib import admin
from .models import WellnessGoal, Goal, GoalProgress

@admin.register(WellnessGoal)
class WellnessGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_text', 'is_completed', 'created_at', 'target_date')
    list_filter = ('is_completed', 'created_at', 'target_date', 'user')
    search_fields = ('goal_text', 'user__username')
    list_editable = ('is_completed',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'text_preview', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text Preview'

@admin.register(GoalProgress)
class GoalProgressAdmin(admin.ModelAdmin):
    list_display = ('goal_preview', 'date', 'completed', 'user')
    list_filter = ('completed', 'date', 'goal__user')
    search_fields = ('goal__text', 'goal__user__username')
    date_hierarchy = 'date'
    ordering = ('-date',)
    
    def goal_preview(self, obj):
        return obj.goal.text[:30] + '...' if len(obj.goal.text) > 30 else obj.goal.text
    goal_preview.short_description = 'Goal'
    
    def user(self, obj):
        return obj.goal.user.username
    user.short_description = 'User'