# File: models.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: urls file to specify routing for mini_fb app.
from django.db import models

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