from django import forms
from .models import MoodEntry

class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood_score', 'note', 'sentiment', 'ai_insight']  # 👈 include ai_insight
        widgets = {
            'mood_score': forms.Select(attrs={
                'class': 'form-control',
                'aria-label': 'Select your mood score',
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any notes about your mood...',
                'aria-label': 'Mood notes',
            }),
            'sentiment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your emotional state...',
                'aria-label': 'Sentiment analysis',
            }),
            'ai_insight': forms.Textarea(attrs={  # 👈 Make it readonly
                'class': 'form-control',
                'rows': 2,
                'readonly': True,
                'placeholder': 'AI-generated insight will appear here after submission...',
                'aria-label': 'AI Insight',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mood_score'].label = "How are you feeling?"
        self.fields['note'].label = "Additional Notes"
        self.fields['sentiment'].label = "Emotional State"
        self.fields['ai_insight'].label = "AI Insight (Gemini)"  # 👈 Label it
        self.fields['mood_score'].help_text = "Select a value from 1 (worst) to 10 (best)"
        self.fields['sentiment'].help_text = "Describe your current emotions in detail"
        self.fields['ai_insight'].required = False
