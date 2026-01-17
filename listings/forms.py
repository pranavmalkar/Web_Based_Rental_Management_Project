from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'address', 'city', 'country', 'category',
            'price_per_night', 'max_guests', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price_per_night': forms.NumberInput(attrs={'min': 0}),
            'max_guests': forms.NumberInput(attrs={'min': 1}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
