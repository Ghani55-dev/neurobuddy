from django.contrib import admin
from .models import EntertainmentVideo, VideoComment, Playlist
from django.utils.html import format_html
@admin.register(EntertainmentVideo)
class EntertainmentVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'upload_date', 'views', 'like_count', 'status')
    list_filter = ('category', 'upload_date', 'status')
    search_fields = ('title', 'description')
    actions = ['approve_selected', 'reject_selected']
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height: 60px;" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = 'Thumbnail'
    
    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'

    def approve_selected(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, "Selected videos have been approved.")
    approve_selected.short_description = "✅ Approve selected videos"

    def reject_selected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Selected videos have been rejected.")
    reject_selected.short_description = "❌ Reject selected videos"
    
@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'text', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'text')
    
admin.site.register(Playlist)


    
