from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
import json
import random

from textblob import TextBlob
import google.generativeai as genai
from django.conf import settings

from .forms import MoodEntryForm
from .models import MoodEntry, MoodSuggestion
from accounts.models import UserProfile
from .utils import generate_insight_from_note

from django.core.mail import send_mail
from twilio.rest import Client
from django.http import JsonResponse
from dashboard.ai_utils import get_daily_suggestion

from .utils import get_current_streak, generate_insight_from_note
from dashboard.ai_utils import generate_and_store_ai_suggestions, get_daily_suggestion

@login_required
def mood_submit_view(request):
    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            mood = form.save(commit=False)
            mood.user = request.user

            # ✨ Sentiment analysis using TextBlob
            if mood.note:
                analysis = TextBlob(mood.note)
                polarity = analysis.sentiment.polarity
                mood.sentiment = (
                    'Positive' if polarity > 0.1 else
                    'Negative' if polarity < -0.1 else
                    'Neutral'
                )
            else:
                mood.sentiment = 'Neutral'

            # ✨ Generate AI insight from mood note (Gemini)
            mood.ai_insight = generate_insight_from_note(mood.note)

            # Save mood entry first
            mood.save()

            # ✅ Generate AI-powered suggestion based on mood_score
            generate_and_store_ai_suggestions(mood_score=mood.mood_score)
            print("🎯 Submitting mood with score:", mood.mood_score)


            return redirect('dashboard')
    else:
        form = MoodEntryForm()

    return render(request, 'mood/mood_form.html', {
        'form': form,
        'streak': get_current_streak(request.user),
        'suggestion': get_daily_suggestion(request.user),
    })



@login_required
def mood_history_view(request):
    moods = MoodEntry.objects.filter(user=request.user).order_by('-date')
    return render(request, 'mood/mood_history.html', {'moods': moods})


@login_required
def mood_chart_view(request):
    today = timezone.now().date()
    last_7_days = today - timedelta(days=6)

    moods = MoodEntry.objects.filter(
        user=request.user,
        date__range=[last_7_days, today]
    ).order_by('date')

    labels = [entry.date.strftime('%b %d') for entry in moods]
    mood_scores = [entry.mood_score for entry in moods]

    return render(request, 'mood/mood_chart.html', {
        'labels': json.dumps(labels),
        'mood_scores': json.dumps(mood_scores)
    })


@login_required
def gpt_mood_summary_view(request):
    today = timezone.now().date()
    last_7_days = today - timedelta(days=6)

    entries = MoodEntry.objects.filter(
        user=request.user,
        date__range=[last_7_days, today]
    ).order_by('date')

    if not entries:
        return render(request, 'mood/gpt_summary.html', {
            'summary': "No mood data available yet. Please start journaling your mood to receive weekly insights."
        })

    if entries.count() == 1:
        entry = entries.first()
        summary = (
            f"You recorded a mood score of {entry.mood_score} on {entry.date}. "
            f"Notes: {entry.note or 'No notes provided.'} "
            "Even one entry is a great start! Keep logging your moods daily to discover trends and insights over time."
        )
        return render(request, 'mood/gpt_summary.html', {'summary': summary})

    # Prepare mood logs
    mood_log = "\n".join([
        f"Date: {entry.date}, Mood Score: {entry.mood_score}, Notes: {entry.note or 'No notes'}"
        for entry in entries
    ])

    prompt = f"""
    You are a compassionate and supportive mental wellness assistant.
    Based on the user's mood entries from the past 7 days, write an empathetic and uplifting 100-word summary.
    Acknowledge patterns in mood scores, offer gentle encouragement, and suggest reflection — even if the data is minimal.
    Mood Logs:\n{mood_log}
    """

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        summary = response.text.strip()
    except Exception as e:
        summary = f"⚠️ Error generating summary: {str(e)}"

    return render(request, 'mood/gpt_summary.html', {'summary': summary})


# Utility to fetch a random daily suggestion
# def get_daily_suggestion():
#     suggestions = MoodSuggestion.objects.all()
#     return random.choice(suggestions) if suggestions.exists() else None


# Utility to calculate user's streak
def get_current_streak(user):
    today = date.today()
    streak = 0
    for i in range(0, 30):
        day = today - timedelta(days=i)
        if MoodEntry.objects.filter(user=user, date=day).exists():
            streak += 1
        else:
            break
    return streak


# mood/views.py


@login_required
def send_emergency_alert(user, mood_entry):
    profile = user.userprofile
    
    # Email alert
    if profile.emergency_contact_email:
        send_mail(
            subject='🚨 Mood Alert: {} needs support'.format(user.username),
            message=f"""{user.username} reported a distressed mood level of {mood_entry.get_mood_score_display()}.
            
            Notes: {mood_entry.note or 'No additional notes'}
            
            Please check on them.
            
            Reply STOP to unsubscribe from alerts.""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.emergency_contact_email],
            fail_silently=False,
        )
    
    # SMS alert
    if profile.emergency_contact_number:
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"""🚨 {user.username} reported distressed mood ({mood_entry.get_mood_score_display()}). 
                Notes: {mood_entry.note or 'None'}. 
                Reply STOP to opt out.""",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=profile.emergency_contact_number
            )
        except Exception as e:
            print(f"Failed to send SMS: {e}")

@login_required
def mood_submit(request):
    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            mood = form.save(commit=False)
            mood.user = request.user
            mood.save()

            # DEBUG: Print critical values
            print(f"\n=== ALERT DEBUG ===")
            print(f"Form mood_score: {form.cleaned_data['mood_score']}")
            print(f"Model mood_score: {mood.mood_score}")
            print(f"User profile exists: {hasattr(request.user, 'userprofile')}")
            
            # Explicit alert check
            if int(form.cleaned_data['mood_score']) <= 2:
                print("Low mood detected - proceeding with alerts")
                try:
                    profile = request.user.userprofile
                    print(f"Emergency contacts - Email: {profile.emergency_contact_email}, Phone: {profile.emergency_contact_number}")
                    
                    if profile.emergency_contact_email:
                        print("Sending email alert")
                        send_mail(
                            subject='🚨 Mood Alert: User Needs Support',
                            message=f"{request.user.username} reported a mood score of {mood.mood_score}",
                            from_email='noreply@yourdomain.com',
                            recipient_list=[profile.emergency_contact_email],
                            fail_silently=False,
                        )
                    
                    mood.alert_sent = True
                    mood.save()
                    # In mood/views.py

                    generate_and_store_ai_suggestions(mood_score=mood.mood_score)

                    print("Alert sent and recorded")
                except Exception as e:
                    print(f"Error in alert sending: {e}")
                    raise

            return redirect('dashboard')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = MoodEntryForm()
    return render(request, 'mood/mood_submit.html', {'form': form})

@login_required
def cancel_alert(request):
    # Get the latest alert that was sent
    latest_alert = MoodEntry.objects.filter(
        user=request.user,
        alert_sent=True
    ).order_by('-date').first()
    
    if latest_alert:
        latest_alert.alert_acknowledged = True
        latest_alert.save()
    
    return JsonResponse({'status': 'acknowledged'})