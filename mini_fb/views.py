# File: views.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: file to specify the views that will handle requests for mini_fb app.
from typing import Any
from django.shortcuts import render, get_object_or_404, redirect

from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin## NEW
from django.contrib.auth.forms import UserCreationForm 
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

    def get_context_data(self, **kwargs):
        """Provide context for both UserCreationForm and CreateProfileForm."""
        create_form = UserCreationForm
        context = super().get_context_data(**kwargs)
        context['create_form'] = create_form  # Add UserCreationForm to the context
        return context
    def form_valid(self, form):
        """Handle submission of both forms together."""
        print(f'CreateProfileView.form_valid(): form.cleaned_data={form.cleaned_data}')
        user_form = UserCreationForm(self.request.POST)
        user = user_form.save()
        form.instance.user = user
        return super().form_valid(form)
class CreateStatusMessageView(LoginRequiredMixin,CreateView):
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"
    def get_login_url(self) -> str:
        '''return the URL of the login page'''
        return reverse('login')
    def get_context_data(self, **kwargs):

        # get the context data from the sueprclass
        context =  super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)        
        # add the Article referred to by the URL into this context
        context['profile'] = profile
        return context
    def form_valid(self, form):
            '''This method is called after the form is validated, 
            before saving data to the database.'''

            files = self.request.FILES.getlist('files')
            print(f'CreateStatusMessageView.form_valid(): form={form.cleaned_data}')
            print(f'CreateStatusMessageView.form_valid(): self.kwargs={self.kwargs}')

            # find the Article identified by the PK from the URL pattern
            profile = Profile.objects.get(user=self.request.user)        
            # attach this Article to the instance of the Comment to set its FK
            form.instance.profile = profile # like: comment.article = article
            sm = form.save() # reference to new sm object 
            for file in files:
                # Create a new Image object for each file
                image = Image()
                image.image_file = file 
                image.status = sm
                image.save()

            # delegate work to superclass version of this method
            return super().form_valid(form)
    def get_success_url(self):
            '''Return the URL to redirect to on success.'''
            # return 'show_all' # a valid URL pattern
            # return reverse('show_all') # look up the URL called "show_all"

            # find the Article identified by the PK from the URL pattern
            profile = Profile.objects.get(user=self.request.user)        
            return reverse('show_profile', kwargs={'pk':profile.pk})
            # return reverse('article', kwargs=self.kwargs)
    def get_object(self):
        '''return matching profile for user'''
        return Profile.objects.get(user=self.request.user)
class UpdateProfileForm(LoginRequiredMixin,UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    
    template_name = 'mini_fb/update_profile_form.html'
    context_object_name = 'profile'
    def get_login_url(self) -> str:
        '''return the URL of the login page'''
        return reverse('login')
    def get_object(self):
        '''return matching profile for user'''
        return Profile.objects.get(user=self.request.user)
class DeleteStatusMessageView(LoginRequiredMixin,DeleteView):
     model = StatusMessage
     template_name = 'mini_fb/delete_status_form.html'
     context_object_name = 'status'
     def get_login_url(self) -> str:
        '''return the URL of the login page'''
        return reverse('login')
     def get_success_url(self) -> str:
          '''Redirect to profile page after deletion'''
          profile = self.object.profile
          return reverse('show_profile', kwargs={'pk': profile.pk})
     
class UpdateStatusMessageView(LoginRequiredMixin,UpdateView):
     model = StatusMessage
     template_name = "mini_fb/update_status_form.html"
     context_object_name = 'status'
     fields=['message']

     def get_success_url(self) -> str:
        '''Redirect to profile page after deletion'''
        profile = self.object.profile
        return reverse('show_profile', kwargs={'pk': profile.pk})
     def get_login_url(self) -> str:
        '''return the URL of the login page'''
        return reverse('login')
class CreateFriendView(LoginRequiredMixin,View):
     def dispatch(self, request, *args, **kwargs):
        other_pk = kwargs['other_pk']
        
        profile = Profile.objects.get(user=self.request.user)
        other_profile = get_object_or_404(Profile, pk=other_pk)
        
        profile.add_friend(other_profile)
        return redirect('show_profile', pk=profile.pk)
     def get_login_url(self) -> str:
        '''return the URL of the login page'''
        return reverse('login')
class ShowFriendSuggestionsView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggestions'] = self.object.get_friend_suggestions()
        return context
    def get_login_url(self) -> str:
        '''return the URL of the login page'''
        return reverse('login')
    def get_object(self):
        '''return matching profile for user'''
        return Profile.objects.get(user=self.request.user)
class ShowNewsFeedView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        profile = self.object  # The Profile instance from the URL
        context['news_feed'] = profile.get_news_feed()  # Call the get_news_feed method
        return context
    def get_login_url(self) -> str:
        '''return the URL of the login page'''
        return reverse('login')
    def get_object(self):
        '''return matching profile for user'''
        return Profile.objects.get(user=self.request.user)
