from django import forms
from .models import WellnessGoal

class WellnessGoalForm(forms.ModelForm):
    class Meta:
        model = WellnessGoal
        fields = ['goal_text', 'target_date']
        widgets = {
            'goal_text': forms.TextInput(attrs={
                'placeholder': 'e.g., Meditate 10 minutes daily',
                'class': 'form-control',
            }),
            'target_date': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'Select your target date',
                'class': 'form-control',
            }),
        }
