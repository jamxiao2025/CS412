# File: urls.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: urls file to specify routing for mini_fb app.
from django.urls import path
from django.conf import settings
from . import views
# all of the URLs that are part of this app
urlpatterns = [
    path(r'', views.ShowAllProfileViews.as_view(), name="show_all"),
]