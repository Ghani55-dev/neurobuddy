from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from requests_oauthlib import OAuth2Session
from .models import WearableData
from datetime import datetime
from django.http import JsonResponse
from .models import WearableData
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from fcm_django.models import FCMDevice
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .alerts import send_emergency_alert
from .models import EmergencyAlert

CLIENT_ID = '23QG4H'
CLIENT_SECRET = 'dd7a0152d8df9e599c2a977ee435e0d2'
REDIRECT_URI = 'http://localhost:8000/wearable/fitbit/callback/'

SCOPE = ['activity','heartrate','sleep','profile']
AUTH_BASE = 'https://www.fitbit.com/oauth2/authorize'
TOKEN_URL = 'https://api.fitbit.com/oauth2/token'

@login_required
def connect_fitbit(request):
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    authorization_url, state = oauth.authorization_url(AUTH_BASE)
    request.session['oauth_state'] = state
    return redirect(authorization_url)

@login_required
def fitbit_callback(request):
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, state=request.session['oauth_state'])
    token = oauth.fetch_token(TOKEN_URL,
                              client_secret=CLIENT_SECRET,
                              authorization_response=request.build_absolute_uri())
    request.session['fitbit_token'] = token

    # Fetch Data
    headers = {'Authorization': f"Bearer {token['access_token']}"}
    hr_data = oauth.get("https://api.fitbit.com/1/user/-/activities/heart/date/today/1d.json", headers=headers).json()
    steps_data = oauth.get("https://api.fitbit.com/1/user/-/activities/steps/date/today/1d.json", headers=headers).json()
    sleep_data = oauth.get("https://api.fitbit.com/1.2/user/-/sleep/date/today.json", headers=headers).json()

    try:
        heart_rate = hr_data['activities-heart'][0]['value']['restingHeartRate']
    except:
        heart_rate = None

    steps = int(steps_data['activities-steps'][0]['value']) if steps_data['activities-steps'] else 0

    try:
        sleep_minutes = sleep_data['summary']['totalMinutesAsleep']
        sleep_hours = round(sleep_minutes / 60, 1)
    except:
        sleep_hours = None

    WearableData.objects.create(
        user=request.user,
        heart_rate=heart_rate,
        steps=steps,
        sleep_hours=sleep_hours,
    )
    # Emergency Trigger
    if heart_rate and heart_rate > 120:
        send_mail(
            subject='⚠️ Emergency Alert: High Heart Rate Detected!',
            message=f"{request.user.username} recorded a high heart rate: {heart_rate} BPM.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False
            
    )
        send_emergency_alert(request.user, heart_rate)
    return render(request, 'wearable/fitbit_success.html', {
        'heart_rate': heart_rate,
        'steps': steps,
        'sleep_hours': sleep_hours,
    })



@login_required
def wearable_chart_data(request):
    data = WearableData.objects.filter(user=request.user).order_by('-collected_at')[:7][::-1]  # Last 7 days
    response = {
        "labels": [entry.collected_at.strftime("%d %b") for entry in data],
        "heart_rates": [entry.heart_rate for entry in data],
        "steps": [entry.steps for entry in data],
        "sleep_hours": [entry.sleep_hours for entry in data],
    }
    return JsonResponse(response)

@api_view(['POST'])
@login_required
def register_device_token(request):
    token = request.data.get('token')
    if token:
        device, created = FCMDevice.objects.get_or_create(
            user=request.user,
            registration_id=token,
            type="android"
        )
        return Response({"status": "Token registered", "new": created})
    return Response({"error": "No token"}, status=400)

@login_required
def emergency_alerts_view(request):
    alerts = EmergencyAlert.objects.filter(user=request.user).order_by('-triggered_at')[:10]
    return render(request, 'wearable/emergency_alerts.html', {'alerts': alerts})
