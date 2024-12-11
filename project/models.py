# File: models.py
# Author: James Xiao (jamxiao@bu.edu), 12/11/2024
# Description: File for defining models
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q

class UserProfile(models.Model):
    '''Represents a user's profile, including basic information and relationships with friends.'''

    # Data fields for user profile
    first_name = models.CharField(max_length=150, blank=True)  # First name of the user
    last_name = models.CharField(max_length=150, blank=True)   # Last name of the user
    email = models.EmailField(unique=True)  # Unique email for the user profile
    profile_image_url = models.URLField(blank=True)  # URL to the user's profile image (optional)

    # ForeignKey to associate a User model (Django's built-in user model) with the profile
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        '''Return the full name of the user (first and last names).'''
        return f"{self.first_name} {self.last_name}"

    def get_friends(self):
        '''Returns a queryset of the UserProfile instances that are friends with this profile.'''
        # Get all accepted friendships where this profile is either the profile or the friend
        friends1 = Friendship.objects.filter(profile=self).values_list('friend', flat=True).filter(status="accepted")
        friends2 = Friendship.objects.filter(friend=self).values_list('profile', flat=True).filter(status="accepted")
        
        # Combine the two friend lists and return the user profiles corresponding to those ids
        allFriends = friends1.union(friends2)
        return UserProfile.objects.filter(pk__in=allFriends)

    def get_pending_friends(self):
        '''Returns a list of UserProfile instances that have pending friend requests to this profile.'''
        # Get all pending friend requests where the user is the "friend" field in the Friendship model
        pending_requests = Friendship.objects.filter(friend=self, status="pending")
        
        # Return the profiles of those users who have sent a friend request
        return [friendship.profile for friendship in pending_requests]

    def accept_friend(self, other):
        '''Accept a pending friend request from another profile or create a new friendship if not already present.'''
        # Look for a pending friendship between the two profiles
        friendship = Friendship.objects.filter(
            profile=other, 
            friend=self, 
            status='pending'
        ).first()  # Only need the first match, as each friendship is unique
        
        if friendship:
            # If a pending friendship exists, update its status to 'accepted'
            friendship.status = 'accepted'
            friendship.save()
            return friendship  # Return the updated friendship object
        else:
            # If no pending friendship exists, create a new 'accepted' friendship
            new_friendship = Friendship.objects.create(
                profile=self,
                friend=other,
                status='accepted'
            )
            return new_friendship  # Return the newly created friendship object

    def reject_friend(self, other):
        '''Reject a pending friend request from another profile.'''
        # Look for a pending friendship where the other profile is the friend
        friendship = Friendship.objects.filter(
            profile=other, 
            friend=self, 
            status='pending'
        ).first()  # Only need the first match
        
        if friendship:
            # If a pending friendship exists, update its status to 'rejected'
            friendship.status = 'rejected'
            friendship.save()
            return friendship  # Return the updated friendship object

    def get_receipts(self):
        '''Returns a queryset of the receipts associated with this profile.'''
        return Receipt.objects.filter(profile=self).order_by('-date_uploaded')

    def get_absolute_url(self):
        '''Returns the URL to the profile page of the user.'''
        return reverse('show_profile', args=[str(self.pk)])

    def get_feed(self):
        '''Returns a combined list of receipts from this user and their friends, sorted by date.'''
        # Get all friends' profiles
        friends = self.get_friends()

        # Start with the current user's receipts
        receipts = list(self.get_receipts())

        # Add each friend's receipts to the list
        for friend in friends:
            receipts.extend(friend.get_receipts())
        
        # Sort all receipts by their upload date in descending order
        receipts.sort(key=lambda x: x.date_uploaded, reverse=True)

        return receipts

    def get_friend_suggestions(self):
        '''Returns a list of suggested friends excluding those with whom the user has pending requests.'''
        # Get the list of the user's current friends
        friends = self.get_friends()
        friends_pk = {friend.pk for friend in friends}
        
        # Get the list of users with whom the current user has pending friend requests
        pending_friend_requests = Friendship.objects.filter(
            status='pending', 
            profile=self
        ).values_list('friend', flat=True)
        
        # Get the list of users who have sent a pending friend request to the current user
        pending_friend_requests_other_way = Friendship.objects.filter(
            status='pending', 
            friend=self
        ).values_list('profile', flat=True)
        
        # Combine the two sets of pending requests
        all_pending_requests = set(pending_friend_requests) | set(pending_friend_requests_other_way)
        if len(all_pending_requests) == 0:
            suggestions = UserProfile.objects.all()
        # Filter out those who are already friends or have a pending request
        suggestions = UserProfile.objects.exclude(pk=self.pk) \
                                        .exclude(pk__in=friends_pk) \
                                        .exclude(pk__in=all_pending_requests)
        return suggestions

    def add_friend(self, other):
        '''Add a new friend by creating a pending friendship or updating an existing pending request.'''
        if self == other:
            raise ValueError("You cannot add yourself as a friend")

        # Check if a friendship already exists (either direction)
        friendship = Friendship.objects.filter(
            (Q(profile=self) & Q(friend=other)) | (Q(profile=other) & Q(friend=self))
        ).first()  # Only need the first match
        
        if friendship:
            # If the friendship exists, update its status to 'pending'
            friendship.status = 'pending'
            friendship.save()
        else:
            # If no friendship exists, create a new pending friendship
            Friendship.objects.create(profile=self, friend=other, status='pending')


class Receipt(models.Model):
    '''Represents a receipt uploaded by a user, including associated items and total spending.'''

    # ForeignKey to associate the receipt with a UserProfile
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='receipts')
    date_uploaded = models.DateTimeField(auto_now_add=True)  # Automatically set the upload date and time
    receipt_data = models.JSONField(encoder=DjangoJSONEncoder)  # Store the parsed receipt data in JSON format
    total_spent = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount spent on the receipt

    def __str__(self):
        '''Return a string representation of the receipt (including its ID and the user's email).'''
        return f"Receipt {self.id} by {self.profile.email}"


class Item(models.Model):
    '''Represents an item in a receipt, including its name, category, quantity, and price.'''

    # ForeignKey to associate the item with a specific receipt
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)  # Name of the item
    category = models.CharField(max_length=50)  # Category of the item (e.g., food, electronics)
    quantity = models.PositiveBigIntegerField(default=1)  # Quantity of the item purchased
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit of the item

    def __str__(self):
        '''Return a string representation of the item (including its name, category, and price).'''
        return f"{self.name} ({self.category}) - {self.price} x {self.quantity}"


class Friendship(models.Model):
    '''Represents a friendship between two users, with its status (pending, accepted, or rejected).'''

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    )

    # ForeignKey fields to link the friendship to two UserProfiles
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='friend_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Status of the friendship
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the friendship is created

    class Meta:
        '''Ensure that there is only one friendship request between any two users.'''
        unique_together = ('profile', 'friend')  # Prevent duplicate friendships (e.g., mutual friends sending requests)

    def __str__(self):
        '''Return a string representation of the friendship (including the email of the profiles and their status).'''
        return f"{self.profile.email} -> {self.friend.email} ({self.status})"
