from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class OwnerSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Enter your first name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Enter your last name')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'OWNER'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class TravellerSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Enter your first name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Enter your last name')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'TRAVELLER'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
