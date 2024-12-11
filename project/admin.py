# File: admin.py
# Author: James Xiao (jamxiao@bu.edu), 12/11/2024
# Description: File for registering our models
from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile, Receipt, Item, Friendship
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Receipt)
admin.site.register(Item)
admin.site.register(Friendship)