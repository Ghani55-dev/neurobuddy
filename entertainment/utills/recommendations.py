from textblob import TextBlob
from entertainment.models import EntertainmentVideo, VideoRecommendation, WatchHistory
from mood.models import MoodEntry

def recommend_videos_based_on_mood(user):
    # Get user's latest mood entry
    latest_mood = MoodEntry.objects.filter(user=user).order_by('-date').first()
    if not latest_mood:
        return EntertainmentVideo.objects.order_by('?')[:5]
    
    # Analyze mood score and notes
    mood_score = latest_mood.mood_score
    notes_analysis = TextBlob(latest_mood.notes).sentiment.polarity if latest_mood.notes else 0
    
    # Determine mood category
    if mood_score <= 3 or notes_analysis < -0.3:
        # User is feeling down - recommend uplifting content
        categories = ['inspirational', 'motivational', 'happy']
    elif mood_score >= 7 or notes_analysis > 0.3:
        # User is feeling good - recommend fun content
        categories = ['funny', 'entertaining', 'exciting']
    else:
        # Neutral mood - recommend relaxing content
        categories = ['relaxing', 'educational', 'calming']
    
    # Get videos in these categories, excluding already watched
    watched_ids = WatchHistory.objects.filter(user=user).values_list('video_id', flat=True)
    recommendations = EntertainmentVideo.objects.filter(
        category__in=categories
    ).exclude(id__in=watched_ids).order_by('-views')[:10]
    
    # Store recommendations
    for video in recommendations:
        VideoRecommendation.objects.create(
            user=user,
            video=video,
            mood_score=mood_score
        )
    
    return recommendations