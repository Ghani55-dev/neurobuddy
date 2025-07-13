# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import EntertainmentVideo, VideoComment, Playlist, PlaylistVideo, WatchHistory, VideoRecommendation
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import VideoUploadForm, CommentForm, ReplyForm
from django.utils import timezone
from .utills.recommendations import recommend_videos_based_on_mood
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import EntertainmentVideo
import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
import datetime
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import F
from django.db.models import Q
from .utils import is_comment_clean
# from.utils import upload_video_to_firebase

class VideoListView(ListView):
    model = EntertainmentVideo
    template_name = 'entertainment/video_list.html'
    context_object_name = 'videos'
    paginate_by = 10

    def get_queryset(self):
        try:
            queryset = EntertainmentVideo.objects.filter(status='approved')
            
            # Search
            query = self.request.GET.get('q')
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(category__icontains=query)
                )

            # Filter by category
            category = self.request.GET.get('category')
            if category and category != 'All':
                queryset = queryset.filter(category__iexact=category)

            # Sort
            sort = self.request.GET.get('sort')
            if sort == 'views':
                queryset = queryset.order_by('-views')
            elif sort == 'oldest':
                queryset = queryset.order_by('upload_date')
            else:
                queryset = queryset.order_by('-upload_date')

            return queryset

        except Exception as e:
            print(f"Database error: {e}")
            return EntertainmentVideo.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', 'All')
        context['sort_option'] = self.request.GET.get('sort', 'latest')
        context['categories'] = EntertainmentVideo.objects.values_list('category', flat=True).distinct()
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('entertainment/partials/video_card.html', context, request=self.request)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)
        
class VideoDetailView(DetailView):
    model = EntertainmentVideo
    template_name = 'entertainment/video_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            video = self.object
            if video:
                # Increment views
                video.views = (video.views or 0) + 1
                video.save(update_fields=['views'])

                # Fetch related videos by same category, exclude current, and remove duplicates
                related_videos = (
                    EntertainmentVideo.objects
                    .filter(
                        Q(category=video.category) & ~Q(id=video.id)
                    )
                    .distinct()[:4]
                )
                context['related_videos'] = related_videos

                # Resume time if user is logged in
                if self.request.user.is_authenticated:
                    history = WatchHistory.objects.filter(
                        user=self.request.user,
                        video=video
                    ).first()
                    context['resume_time'] = history.progress if history else 0
                else:
                    context['resume_time'] = 0
            else:
                context['related_videos'] = []
                context['resume_time'] = 0

        except Exception as e:
            print(f"[VideoDetailView] Error: {e}")
            context['related_videos'] = []
            context['resume_time'] = 0

        return context

@require_POST
@login_required
def like_video(request):
    video_id = request.POST.get('video_id')
    video = EntertainmentVideo.objects.get(id=video_id)

    if request.user in video.likes.all():
        video.likes.remove(request.user)
        liked = False
    else:
        video.likes.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': video.total_likes()
    })


@login_required
@require_http_methods(["GET", "POST"])
@csrf_exempt  # only if you must (avoid in production; use CSRF token instead)
def upload_video(request):
    if request.method == 'GET':
        return render(request, 'entertainment/upload_video.html')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        duration = request.POST.get('duration')
        video_file = request.FILES.get('video_file')

        if not all([title, category, duration, video_file]):
            return JsonResponse({'error': 'Missing required fields.'}, status=400)

        try:
            EntertainmentVideo.objects.create(
                title=title,
                description=description or "",
                category=category,
                duration=int(duration),
                video_file=video_file,
                uploaded_by=request.user,
                status='pending'
            )
            return JsonResponse({
                'message': 'Upload successful!',
                'redirect_url': reverse('entertainment:upload_success')
            })

        except Exception as e:
            return JsonResponse({'error': f'Error saving video: {str(e)}'}, status=500)


@login_required
def add_comment(request, video_id):
    video = get_object_or_404(EntertainmentVideo, id=video_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_text = form.cleaned_data['text']

            # AI content moderation
            if not is_comment_clean(comment_text):
                messages.warning(request, "Your comment contains inappropriate content and wasn't posted.")
                return redirect('entertainment:video_detail', video_id)

            comment = form.save(commit=False)
            comment.video = video
            comment.user = request.user
            comment.save()

            messages.success(request, "Your comment was added successfully.")
        else:
            messages.error(request, "There was an error with your comment.")
    
    return redirect('entertainment:video_detail', video_id)

@login_required
def add_reply(request, comment_id):
    parent_comment = get_object_or_404(VideoComment, id=comment_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.video = parent_comment.video
            reply.user = request.user
            reply.parent = parent_comment
            reply.save()
    return redirect('video_detail', pk=parent_comment.video.id)

def shared_video(request, token):
    video = get_object_or_404(EntertainmentVideo, share_token=token)
    return render(request, 'entertainment/shared_video.html', {'video': video})

# views.py
@login_required
def create_playlist(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        playlist = Playlist.objects.create(
            user=request.user,
            title=title,
            description=description
        )
        return redirect('playlist_detail', playlist_id=playlist.id)
    return render(request, 'entertainment/create_playlist.html')

@login_required
def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    return render(request, 'entertainment/playlist_detail.html', {'playlist': playlist})

@login_required
def add_to_playlist(request, video_id):
    video = get_object_or_404(EntertainmentVideo, id=video_id)
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist_id')
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        
        # Get next position in playlist
        last_position = playlist.playlistvideo_set.aggregate(models.Max('position'))['position__max'] or 0
        
        PlaylistVideo.objects.create(
            playlist=playlist,
            video=video,
            position=last_position + 1
        )
        return redirect('video_detail', pk=video_id)
    
    # GET request - show available playlists
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'entertainment/add_to_playlist.html', {
        'video': video,
        'playlists': playlists
    })
    
# views.py
class VideoDetailView(DetailView):
    model = EntertainmentVideo
    template_name = 'entertainment/video_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.object
        
        # Track view count
        video.views += 1
        video.save()
        
        # Update watch history
        if self.request.user.is_authenticated:
            WatchHistory.objects.update_or_create(
                user=self.request.user,
                video=video,
                defaults={'watched_at': timezone.now()}
            )
        
        context['related_videos'] = EntertainmentVideo.objects.filter(
            category=video.category
        ).exclude(id=video.id)[:4]
        
        # Get resume time if exists
        if self.request.user.is_authenticated:
            history = WatchHistory.objects.filter(
                user=self.request.user,
                video=video
            ).first()
            context['resume_time'] = history.progress if history else 0
        
        return context
    

@login_required
def watch_history(request):
    videos = EntertainmentVideo.objects.filter(uploaded_by=request.user)
    return render(request, 'entertainment/watch_history.html', {'videos': videos})

@login_required
def update_progress(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        progress = request.POST.get('progress')
        
        video = get_object_or_404(EntertainmentVideo, id=video_id)
        WatchHistory.objects.update_or_create(
            user=request.user,
            video=video,
            defaults={
                'watched_at': timezone.now(),
                'progress': progress
            }
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)



# class DashboardView(LoginRequiredMixin, TemplateView):
#     template_name = 'dashboard.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Get mood data for charts
#         # ... existing code ...
        
#         # Get personalized recommendations
#         context['recommended_videos'] = recommend_videos_based_on_mood(self.request.user)
        
#         return context

@login_required
def video_clicked(request, recommendation_id):
    recommendation = get_object_or_404(VideoRecommendation, id=recommendation_id, user=request.user)
    recommendation.clicked = True
    recommendation.save()
    return redirect('video_detail', pk=recommendation.video.id)

@login_required
def upload_success(request):
    return render(request, 'entertainment/success.html', {
        'message': '✅ Video Uploaded Successfully!',
        'details': 'Your video has been uploaded and saved in the system.'
    })

# def upload_video(request):
#     if request.method == 'POST' and request.FILES['video']:
#         file = request.FILES['video']
#         firebase_url = upload_video_to_firebase(file)
#         EntertainmentVideo.objects.create(
#             title=request.POST.get('title'),
#             video_url=firebase_url,
#             status='pending',  # for Step 2
#             uploaded_by=request.user
#         )
#         return redirect('video_list')

class VideoFeedView(ListView):
    model = EntertainmentVideo
    template_name = 'entertainment/video_feed.html'
    context_object_name = 'videos'

    def get_queryset(self):
        return EntertainmentVideo.objects.filter(status='approved').order_by('-upload_date')