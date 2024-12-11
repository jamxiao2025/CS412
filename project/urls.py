# File: urls.py
# Author: James Xiao (jamxiao@bu.edu), 12/10/2024
# Description: urls file to specify routing for final project app.
from django.urls import path
from django.conf import settings
from . import views
# all of the URLs that are part of this app
from django.contrib.auth import views as auth_views

urlpatterns = [
    path(r'', views.ShowAllUserProfileViews.as_view(), name="show_all"),
    path(r'create_profile', views.CreateProfileView.as_view(), name='create_profile'),
    path(r'profile/<int:pk>', views.ShowUserProfilePageView.as_view(), name="show_profile"),
    path(r'profile/<int:pk>/items', views.ProfileItemsView.as_view(), name='show_items'),
    path(r'profile/<int:pk>/shopping_analytics', views.ShoppingAnalyticsView.as_view(), name='shopping_analytics'),
    path(r'profile/<int:pk>/leaderboard', views.LeaderboardView.as_view(), name='leaderboard'),
    path(r'receipt/<int:pk>', views.ShowReceiptPageView.as_view(), name="show_receipt"),
    path(r'receipt/<int:pk>/delete_receipt', views.DeleteReceiptPageView.as_view(), name="delete_receipt"),
    path(r'profile/update/<int:pk>', views.UpdateUserProfileForm.as_view(), name='update_profile'),
    path(r'profile/accept_friend/<int:pk>/<int:friend_pk>', views.AcceptFriendView.as_view(), name='accept_friend'),
    path(r'profile/reject_friend/<int:pk>/<int:friend_pk>', views.RejectFriendView.as_view(), name='reject_friend'),
    path(r'profile/<int:pk>/friend_suggestions', views.ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
    path(r'profile/<int:pk>/feed', views.ShowFeedView.as_view(), name='show_feed'),
    path(r'profile/<int:pk>/add_friend/<int:other_pk>/', views.AddFriendView.as_view(), name='add_friend'),
    path(r'profile/<int:pk>/upload_receipt', views.UploadReceiptView.as_view(), name='upload_receipt'),
    path(r'login', auth_views.LoginView.as_view(template_name="project/login.html"), name="login"),
    path(r'logout', auth_views.LogoutView.as_view(template_name="project/logged_out.html"), name="logout")
]