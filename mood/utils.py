import google.generativeai as genai
from django.conf import settings
from mood.models import MoodPrediction
import joblib
import numpy as np

from datetime import date, timedelta
from .models import MoodEntry

def generate_insight_from_note(note):
    if not note:
        return "No specific note provided today."

    prompt = f"Provide a short, friendly mental health tip based on this journal note:\n\n{note}"
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Could not generate insight. Try again later."


def predict_mood_and_save(user, heart_rate, steps, sleep_hours):
    model = joblib.load('mood_predictor.pkl')
    features = np.array([[heart_rate, steps, sleep_hours]])
    predicted = round(model.predict(features)[0], 2)
    
    MoodPrediction.objects.create(
        user=user,
        predicted_score=predicted,
        heart_rate=heart_rate,
        steps=steps,
        sleep_hours=sleep_hours
    )
    return predicted



def get_current_streak(user):
    today = date.today()
    streak = 0

    for days_back in range(0, 100):  # check up to 100 days
        check_date = today - timedelta(days=days_back)
        if MoodEntry.objects.filter(user=user, date=check_date).exists():
            streak += 1
        else:
            break

    return streak
