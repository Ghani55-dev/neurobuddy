from django import forms
from .models import EntertainmentVideo, VideoComment

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = EntertainmentVideo
        fields = ['title', 'description', 'video_file', 'category', 'duration']
        
    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            # Validate file size (e.g., 100MB limit)
            if video_file.size > 100*1024*1024:
                raise forms.ValidationError("File too large (max 100MB)")
            return video_file
        raise forms.ValidationError("Couldn't read uploaded file")
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = VideoComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Add a comment...',
                'class': 'form-control'
            })
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = VideoComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Write a reply...'})
        }
        