from datetime import date
import random
from django.conf import settings
from mood.models import MoodEntry, MoodSuggestion
from wearable.models import WearableData
from accounts.models import UserProfile  # Ensure correct import
import google.generativeai as genai
from .models import SuggestionFeedback
from django.db.models import Q 
from dashboard.youtube_utils import fetch_youtube_video

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_daily_suggestion(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Return existing suggestion if already assigned today
    if profile.last_suggestion_date == date.today() and profile.last_suggestion:
        return profile.last_suggestion

    # Collect latest data
    mood = MoodEntry.objects.filter(user=user, date=date.today()).first()
    wearable = WearableData.objects.filter(user=user, collected_at__date=date.today()).first()

    # Default fallback suggestion
    suggestion = MoodSuggestion.objects.order_by("?").first()

    # Rule-based suggestion
    if mood:
        if mood.mood_score <= 2:
            suggestion = MoodSuggestion.objects.filter(category="quote").order_by("?").first()
        elif mood.mood_score <= 4:
            suggestion = MoodSuggestion.objects.filter(category="tip").order_by("?").first()
        else:
            suggestion = MoodSuggestion.objects.filter(category="video").order_by("?").first()
    elif wearable:
        if wearable.heart_rate and wearable.heart_rate > 120:
            suggestion = MoodSuggestion.objects.filter(category="tip").order_by("?").first()
        elif wearable.sleep_hours and wearable.sleep_hours < 5:
            suggestion = MoodSuggestion.objects.filter(category="quote").order_by("?").first()
        elif wearable.steps and wearable.steps < 3000:
            suggestion = MoodSuggestion.objects.filter(category="video").order_by("?").first()

    # Save for reuse today
    profile.last_suggestion = suggestion
    profile.last_suggestion_date = date.today()
    profile.save()

    return suggestion


def get_all_suggestions(user):
    """
    Returns one suggestion of each category (quote, tip, video).
    Useful to display all types in dashboard.
    """
    return {
        "quote": MoodSuggestion.objects.filter(category="quote").order_by("?").first(),
        "tip": MoodSuggestion.objects.filter(category="tip").order_by("?").first(),
        "video": MoodSuggestion.objects.filter(category="video").order_by("?").first()
    }


genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_and_store_ai_suggestions(mood_score=None):
    if mood_score is None:
        return

    prompt = f"""
    The user has a mood score of {mood_score}/5.
    
    Based on this mood score, generate:
    1. A motivational quote
    2. A helpful mental wellness tip
    3. A YouTube video link (embed format) that can uplift or calm them

    Format:
    Quote: ...
    Tip: ...
    Video: ...
    """
    print("🔁 Calling Gemini with mood score:", mood_score)
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
        response = model.generate_content(prompt)
        print("🔍 Gemini response:\n", response.text)

        if not response or not response.text:
            return

        quote, tip, video_url = None, None, None
        for line in response.text.split("\n"):
            if line.lower().startswith("quote:"):
                quote = line.split(":", 1)[1].strip()
            elif line.lower().startswith("tip:"):
                tip = line.split(":", 1)[1].strip()
            elif line.lower().startswith("video:"):
                video_url = line.split(":", 1)[1].strip()

        if quote:
            MoodSuggestion.objects.create(category="quote", content=quote, source="AI")
        if tip:
            MoodSuggestion.objects.create(category="tip", content=tip, source="AI")
        if video_url:
            MoodSuggestion.objects.create(category="video", content="Watch this video!", video_url=video_url, source="AI")

        print("✅ Suggestions saved successfully.")

    except Exception as e:
        print("❌ Error generating or saving suggestions:", e)


def get_personalized_suggestions(user):
    # Get user's most recent mood entry
    latest_mood = MoodEntry.objects.filter(user=user).order_by('-date').first()
    
    if not latest_mood:
        # If no mood entries, return default suggestions
        return get_default_suggestions()
    
    mood_score = latest_mood.mood_score
    
    # Define suggestion filters based on mood
    if mood_score <= 2:  # Low mood
        quote_filter = Q(category='quote', content__icontains='hope') | Q(category='quote', content__icontains='strength')
        tip_filter = Q(category='tip', content__icontains='self-care') | Q(category='tip', content__icontains='comfort')
        video_filter = Q(category='video', content__icontains='calming') | Q(category='video', content__icontains='relax')
    elif mood_score == 3:  # Neutral mood
        quote_filter = Q(category='quote', content__icontains='motivation') | Q(category='quote', content__icontains='inspiration')
        tip_filter = Q(category='tip', content__icontains='productivity') | Q(category='tip', content__icontains='balance')
        video_filter = Q(category='video', content__icontains='motivational') | Q(category='video', content__icontains='inspiration')
    else:  # High mood (4-5)
        quote_filter = Q(category='quote', content__icontains='success') | Q(category='quote', content__icontains='achievement')
        tip_filter = Q(category='tip', content__icontains='growth') | Q(category='tip', content__icontains='positive')
        video_filter = Q(category='video', content__icontains='happy') | Q(category='video', content__icontains='energy')
    
    # Get suggestions that haven't been shown to this user before
    shown_suggestions = SuggestionFeedback.objects.filter(user=user).values_list('suggestion_id', flat=True)
    
    # Get one suggestion of each type
    quote = MoodSuggestion.objects.filter(quote_filter).exclude(id__in=shown_suggestions).order_by('?').first()
    tip = MoodSuggestion.objects.filter(tip_filter).exclude(id__in=shown_suggestions).order_by('?').first()
    video = MoodSuggestion.objects.filter(video_filter).exclude(id__in=shown_suggestions).order_by('?').first()
    
    # If no new suggestions found, get any random one
    if not quote:
        quote = MoodSuggestion.objects.filter(category='quote').exclude(id__in=shown_suggestions).order_by('?').first()
    if not tip:
        tip = MoodSuggestion.objects.filter(category='tip').exclude(id__in=shown_suggestions).order_by('?').first()
    if not video:
        video = MoodSuggestion.objects.filter(category='video').exclude(id__in=shown_suggestions).order_by('?').first()
    
    return {
        'quote': quote,
        'tip': tip,
        'video': video
    }

def get_default_suggestions():
    """Return default suggestions when no mood data is available"""
    return {
        'quote': MoodSuggestion.objects.filter(category='quote').order_by('?').first(),
        'tip': MoodSuggestion.objects.filter(category='tip').order_by('?').first(),
        'video': MoodSuggestion.objects.filter(category='video').order_by('?').first()
    }