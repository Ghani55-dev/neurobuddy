from fcm_django.models import FCMDevice
from firebase_admin import messaging
from .models import EmergencyAlert  

def send_emergency_alert(user, heart_rate):
    devices = FCMDevice.objects.filter(user=user)

    # Save alert to DB
    EmergencyAlert.objects.create(
        user=user,
        alert_type='High Heart Rate',
        message=f'Detected heart rate of {heart_rate} BPM.'
    )

    for device in devices:
        if device.registration_id:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="🚨 High Heart Rate!",
                    body=f"Detected: {heart_rate} BPM. Please take care.",
                ),
                token=device.registration_id,
            )
            response = messaging.send(message)
            print('✅ Firebase push sent:', response)

