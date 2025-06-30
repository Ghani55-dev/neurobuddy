from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
from mood.models import MoodEntry
from accounts.models import UserProfile

class EmergencyAlertTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Ganesh', password='Ghani@55')
        self.profile = UserProfile.objects.create(
            user=self.user,
            emergency_contact_email='ganaganigana03@gmail.com',
            emergency_contact_number='+919014066807'
        )
    

    @patch('mood.views.send_mail')
    def test_alert_triggered_on_low_mood(self, mock_send_mail):
    
    # Ensure user profile has emergency contact
       self.user = User.objects.create_user(username='Ghani', password='ganesh@55')
       self.profile =UserProfile.objects.create(
                         user=self.user,
                         emergency_contact_email='ganaganigana03@gmail.com',
                         emergency_contact_number='+919908004940'
                         )
       self.profile.save()
    # Verify profile is set up correctly
       print("\n=== TEST SETUP ===")
       print(f"Profile email: {self.profile.emergency_contact_email}")
       print(f"Profile phone: {self.profile.emergency_contact_number}")

    
    # Login and get CSRF token
       self.client.login(username='Ganesh', password='Ghani@55')
       get_response = self.client.get(reverse('mood_submit'))
       csrf_token = get_response.context['csrf_token']
    
    # Submit low mood (score 1)
       response = self.client.post(reverse('mood_submit'), {
        'mood_score': '1',  # Very Distressed
        'note': 'Feeling terrible',
        'csrfmiddlewaretoken': csrf_token
    }, follow=True)
    
    # Debugging prints
       print("Response status:", response.status_code)
       mood_entry = MoodEntry.objects.first()
       print("\n=== DEBUG OUTPUT ===")
       print(f"Mood entry created: {mood_entry}")
       print(f"Mood score: {mood_entry.mood_score if mood_entry else 'None'}")
       print(f"Alert sent: {mood_entry.alert_sent if mood_entry else 'None'}")
       print(f"Alert sent flag: {mood_entry.alert_sent}")
       print(f"Email called: {mock_send_mail.called}")
       print(f"Call args: {mock_send_mail.call_args if mock_send_mail.called else 'Not called'}")
       if mood_entry:
           print("Mood score:", mood_entry.mood_score)
           print("Alert sent:", mood_entry.alert_sent)
    
    # Verify alerts were sent
       self.assertTrue(mock_send_mail.called, 
                  "Email alert should have been sent for mood score 1")
       self.assertTrue(mock_send_mail.called, 
                  f"Email not sent. Mock calls: {mock_send_mail.call_args_list}")
    # Verify mood entry was created with alert
       self.assertEqual(mood_entry.mood_score, 1)
       self.assertTrue(mood_entry.alert_sent)
    # @patch('mood.views.Client')
    # @patch('mood.views.send_mail')
    # def test_no_alert_for_high_mood(self, mock_send_mail, mock_twilio_client):
    #     mock_client_instance = MagicMock()
    #     mock_twilio_client.return_value = mock_client_instance
        
    #     self.client.login(username='testuser', password='pass123')
    #     response = self.client.get(reverse('mood_submit'))
    #     csrf_token = response.context['csrf_token']
        
    #     response = self.client.post(reverse('mood_submit'), {
    #         'mood_score': '4',  # Good
    #         'notes': 'Feeling okay',
    #         'csrfmiddlewaretoken': csrf_token
    #     }, follow=True)
        
    #     self.assertFalse(mock_send_mail.called)
    #     self.assertFalse(mock_client_instance.messages.create.called)
    #     mood_entry = MoodEntry.objects.first()
    #     self.assertFalse(mood_entry.alert_sent)
    
    def test_cancel_alert_endpoint(self):
        # Create a mood entry with alert
        MoodEntry.objects.create(
            user=self.user,
            mood_score=1,
            alert_sent=True,
            alert_acknowledged=False
        )
        
        self.client.login(username='Ganesh', password='Ghani@55')
        response = self.client.get(reverse('cancel_alert'))
        
        self.assertEqual(response.status_code, 200)
        mood_entry = MoodEntry.objects.first()
        self.assertTrue(mood_entry.alert_acknowledged)