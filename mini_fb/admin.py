# File: admin.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: file to add model to admin
from django.contrib import admin
from .models import Profile, StatusMessage, Image, Friend
# Register your models here.
admin.site.register(Profile)
admin.site.register(StatusMessage)
admin.site.register(Image)
admin.site.register(Friend)