from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for submitting / editing a review."""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),  # Controlled by JS star widget
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your thoughts about this card...'
            }),
        }
