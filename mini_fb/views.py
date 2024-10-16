# File: views.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: file to specify the views that will handle requests for mini_fb app.
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import * 
from .forms import * 
# Create your views here.
class ShowAllProfileViews(ListView):
    '''The view to show all Profiles'''
    model = Profile 
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name ='profiles'

class ShowProfilePageView(DetailView):
    '''The view to show a Profile'''
    model = Profile 
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

class CreateProfileView(CreateView):
    '''The view to create a Profile'''
    form_class = CreateProfileForm
    template_name = "mini_fb/create_profile_form.html"

class CreateStatusMessageView(CreateView):
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_message_form.html"
    def get_context_data(self, **kwargs):

        # get the context data from the sueprclass
        context =  super().get_context_data(**kwargs)

        # find the Article identified by the PK from the URL pattern
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        
        # add the Article referred to by the URL into this context
        context['profile'] = profile
        return context
    def form_valid(self, form):
            '''This method is called after the form is validated, 
            before saving data to the database.'''

            print(f'CreateStatusMessageView.form_valid(): form={form.cleaned_data}')
            print(f'CreateStatusMessageView.form_valid(): self.kwargs={self.kwargs}')

            # find the Article identified by the PK from the URL pattern
            profile = Profile.objects.get(pk=self.kwargs['pk'])

            # attach this Article to the instance of the Comment to set its FK
            form.instance.profile = profile # like: comment.article = article

            # delegate work to superclass version of this method
            return super().form_valid(form)
    def get_success_url(self):
            '''Return the URL to redirect to on success.'''
            # return 'show_all' # a valid URL pattern
            # return reverse('show_all') # look up the URL called "show_all"

            # find the Article identified by the PK from the URL pattern
            profile = Profile.objects.get(pk=self.kwargs['pk'])
            return reverse('show_profile', kwargs={'pk':profile.pk})
            # return reverse('article', kwargs=self.kwargs)