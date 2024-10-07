from django.shortcuts import render
from django.views.generic import ListView
from .models import * 
# Create your views here.
class ShowAllProfileViews(ListView):
    '''The view to show all Profiles'''
    model = Profile 
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name ='profiles'