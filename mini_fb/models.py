# File: models.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: urls file to specify routing for mini_fb app.
from django.db import models
from django.utils import timezone
from django.urls import reverse
class Profile(models.Model):
    '''Encapsulates a profile'''

    # data attributes of a Profile
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=False)
    profile_image_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_status_messages(self):
        '''Return the status messages associated with this profile'''
        status_messages = StatusMessage.objects.filter(profile=self)
        return status_messages
    def get_absolute_url(self):
        return reverse('show_profile', args=[str(self.pk)])

class StatusMessage(models.Model):
    '''Encapsulates a status message'''
    timestamp = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=False)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.message} at {self.timestamp}"
