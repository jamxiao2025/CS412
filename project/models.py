from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q

class UserProfile(models.Model):
    '''Encapsulates a profile'''
    # data attributes 
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    profile_image_url = models.URLField(blank=True)

    # User foreign key
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    def get_friends(self):
        '''Returns the friends that this profile has
        '''
        friends1 = Friendship.objects.filter(profile=self).values_list('friend', flat=True).filter(status="accepted")
        friends2 = Friendship.objects.filter(friend=self).values_list('profile', flat=True).filter(status="accepted")
        allFriends = friends1.union(friends2)
        return UserProfile.objects.filter(pk__in=allFriends)
    def get_pending_friends(self):
        '''Returns the pending friend requests where the user is in the "friend" field of the Friendship model.'''
    
        # Get all pending friend requests where the user is the "friend"
        pending_requests = Friendship.objects.filter(friend=self, status="pending")
        
        # Return the list of profiles that have sent a friend request to this user
        return [friendship.profile for friendship in pending_requests]

    def accept_friend(self, other):
        friendship = Friendship.objects.filter(
            profile=self, 
            friend=other, 
            status='pending'
        ).first()  # We only need the first one, since we are ensuring unique pairs
        
        # If a pending friendship exists, we can accept it
        if friendship:
            # Update the status of the pending friendship to 'accepted'
            friendship.status = 'accepted'
            friendship.save()
            return friendship  # Return the accepted friendship object
        
        # If no friendship exists (e.g., no pending request), create a new one
        else:
            # Create a new friendship from the current profile to the other user
            new_friendship = Friendship.objects.create(
                profile=self,
                friend=other,
                status='accepted'
            )
            return new_friendship  # Return the newly created friendship object
    def reject_friend(self, other):
        friendship = Friendship.objects.filter(
            profile=other, 
            friend=self, 
            status='pending'
        ).first()  # We only need the first one, since we are ensuring unique pairs
        
        # If a pending friendship exists, we can accept it
        if friendship:
            # Update the status of the pending friendship to 'accepted'
            friendship.status = 'rejected'
            friendship.save()
            return friendship  # Return the accepted friendship object
        
    def get_receipts(self):
        return Receipt.objects.filter(profile=self) 
    def get_absolute_url(self):
        return reverse('show_profile', args=[str(self.pk)])
    def get_feed(self):
        # Get all friends' profiles
        friends = self.get_friends()
        
        # Start with the current user's status messages
        receipts = list(self.get_receipts())

        # Extend with friends' status messages
        for friend in friends:
            receipts.extend(friend.get_receipts())
        
        # Sort the status messages by timestamp, most recent first
        receipts.sort(key=lambda x: x.date_uploaded, reverse=True)

        return receipts
    def get_friend_suggestions(self):
        '''Return a list of suggested friends excluding those with whom the user has a pending request'''
        
        # Get the list of already friends
        friends = self.get_friends() 
        friends_pk = {friend.pk for friend in friends}
        
        # Get the list of users the current user has a pending request with
        pending_friend_requests = Friendship.objects.filter(
            status='pending', 
            profile=self
        ).values_list('friend', flat=True)  # Get the PKs of the friends with pending requests
        
        # Similarly, exclude users who have a pending friend request towards the current user
        pending_friend_requests_other_way = Friendship.objects.filter(
            status='pending', 
            friend=self
        ).values_list('profile', flat=True)  # Get the PKs of users who have sent a pending request to the current user
        
        # Combine both pending request lists
        all_pending_requests = set(pending_friend_requests) | set(pending_friend_requests_other_way)
        
        # Now filter out those with pending requests and the already existing friends
        suggestions = UserProfile.objects.exclude(pk=self.pk) \
                                        .exclude(pk__in=friends_pk) \
                                        .exclude(pk__in=all_pending_requests)
        return suggestions
    def add_friend(self, other):
        '''Method for adding friends. Updates existing friendships or creates new pending requests.'''
        
        if self == other:
            raise ValueError("You cannot add yourself as a friend")
        
        # Check if a friendship already exists in either direction
        friendship = Friendship.objects.filter(
            (Q(profile=self) & Q(friend=other)) | (Q(profile=other) & Q(friend=self))
        ).first()  # Get the first match if it exists
        
        if friendship:
            friendship.status = 'pending'
            friendship.save()
        else:
            # If no friendship exists, create a new pending friendship
            Friendship.objects.create(profile=self, friend=other, status='pending')

class Receipt(models.Model):
    '''Encapsulates a receipt in JSON string'''
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='receipts')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    receipt_data = models.JSONField(encoder=DjangoJSONEncoder)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
            return f"Receipt {self.id} by {self.profile.username}"

class Item(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.price} x {self.quantity}"
    
class Friendship(models.Model):
     STATUS_CHOICES = (
          ('pending', 'Pending'),
          ('accepted', 'Accepted'),
          ('rejected', 'Rejected')
     )
     profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='friendships')
     friend = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='friend_requests')
     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
     created_at = models.DateTimeField(auto_now_add=True)
     class Meta:
        unique_together = ('profile', 'friend')  # Prevent duplicate friend requests
     def __str__(self):
        return f"{self.profile.username} -> {self.friend.username} ({self.status})"
