from django import forms
from .models import UserProfile

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['emergency_contact_email', 'emergency_contact_number']