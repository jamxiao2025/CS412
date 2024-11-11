# File: urls.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: urls file to specify routing for mini_fb app.
from django.urls import path
from .views import VoterListView, VoterDetailView, GraphView

# all of the URLs that are part of this app
urlpatterns = [
    path(r'', VoterListView.as_view(), name="home"),
    path(r'voters', VoterListView.as_view(), name="voters"),
    path('voter/<int:pk>/', VoterDetailView.as_view(), name='voter'),  # Single voter detail
    path('graphs/', GraphView.as_view(), name='graphs'),
]