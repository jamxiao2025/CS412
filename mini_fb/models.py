# File: models.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: urls file to specify routing for mini_fb app.
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

class Profile(models.Model):
    '''Encapsulates a profile'''

    # data attributes of a Profile
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

    def get_friends(self):
        '''Returns the friends that this profile has
        '''
        friends1 = Friend.objects.filter(profile1=self).values_list('profile2', flat=True)
        friends2 = Friend.objects.filter(profile2=self).values_list('profile1', flat=True)
        allFriends = friends1.union(friends2)
        return Profile.objects.filter(pk__in=allFriends)
        
    def add_friend(self, other):
        '''Method for adding friends
        '''
        if self == other:
            raise ValueError("You cannot add yourself as a friend")
        # Check if friendship already exists
        existing_friend = Friend.objects.filter(
            models.Q(profile1 = self, profile2 = other) | models.Q(profile1 = other, profile2 = self)
        ).first()
        if not existing_friend:
            Friend.objects.create(profile1=self, profile2=other)
    def get_friend_suggestions(self):
        '''Return a list of suggested friends
        '''
        friends = self.get_friends() 
        friends_pk = {friend.pk for friend in friends}
        suggestions = Profile.objects.exclude(pk=self.pk).exclude(pk__in=friends_pk)
        return suggestions
    def get_news_feed(self):
        # Get all friends' profiles
        friends = self.get_friends()
        
        # Start with the current user's status messages
        status_messages = list(self.get_status_messages())

        # Extend with friends' status messages
        for friend in friends:
            status_messages.extend(friend.get_status_messages())
        
        # Sort the status messages by timestamp, most recent first
        status_messages.sort(key=lambda x: x.timestamp, reverse=True)

        return status_messages
class StatusMessage(models.Model):
    '''Encapsulates a status message'''
    timestamp = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=False)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.message} at {self.timestamp}"
    
    def get_images(self):
        return Image.objects.filter(status=self)

class Image(models.Model):
    ''' Model to represent an image associated with a status message
    '''
    image_file = models.ImageField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    status = models.ForeignKey('StatusMessage', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.status} at {self.timestamp}"
    
class Friend(models.Model):
    '''Model to represent an edge connecting two nodes (friends)
    '''
    profile1 = models.ForeignKey(Profile, related_name="profile1", on_delete=models.CASCADE)
    profile2 = models.ForeignKey(Profile, related_name="profile2", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profile1} & {self.profile2}"