from django import forms
from .models import Profile, StatusMessage

class CreateProfileForm(forms.ModelForm):
    '''A form to create a profile'''
    class Meta:
        model = Profile 
        fields = ['first_name', 'last_name', 'city', 'email', 'address', 'profile_image_url']


class CreateStatusMessageForm(forms.ModelForm):
    '''A form to create a status message'''
    class Meta:
        model = StatusMessage
        fields = ['message']