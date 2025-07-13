from django.urls import path
from . import views
from .views import VideoFeedView
app_name = 'entertainment'

urlpatterns = [
    # Video Listing and Details
    path('', views.VideoListView.as_view(), name='video_list'),
    path('video/<int:pk>/', views.VideoDetailView.as_view(), name='video_detail'),
    
    # Video Interactions
    path('upload/', views.upload_video, name='upload_video'),
    path('like/', views.like_video, name='like_video'),
    path('share/<uuid:token>/', views.shared_video, name='shared_video'),
    path('success/', views.upload_success, name='upload_success'),
    path('history/', views.watch_history, name='watch_history'),
    path('reels/', VideoFeedView.as_view(), name='video_feed'),
    # Comments System
    path('<int:video_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    
    # Playlist Management
    path('playlists/create/', views.create_playlist, name='create_playlist'),
    path('playlists/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('<int:video_id>/add-to-playlist/', views.add_to_playlist, name='add_to_playlist'),
    
    # Viewing History
    path('history/', views.watch_history, name='watch_history'),
    path('update-progress/', views.update_progress, name='update_progress'),
    
    # Recommendations
    path('recommendation/<int:recommendation_id>/click/', views.video_clicked, name='video_clicked'),
    
    # Dashboard (if in same app)
    # path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]