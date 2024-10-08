# File: views.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: file to specify the views that will handle requests for mini_fb app.
from django.shortcuts import render
from django.views.generic import ListView
from .models import * 

# Create your views here.
class ShowAllProfileViews(ListView):
    '''The view to show all Profiles'''
    model = Profile 
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name ='profiles'