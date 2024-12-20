# File: views.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: file to specify the views that will handle requests for mini_fb app.
from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from .models import UserProfile, Receipt, Friendship, Item
from .forms import UpdateUserProfileForm, ReceiptUploadForm, CreateProfileForm
from django.contrib.auth.forms import UserCreationForm
import base64
import json
import datetime
import plotly.express as px
import pandas as pd
from django.db.models import Sum, F, Q
from openai import OpenAI

class CreateProfileView(CreateView):
    '''A view for creating a user profile along with the user creation form.'''

    # Form for creating a user profile
    form_class = CreateProfileForm
    # The template used to render the user creation form
    template_name = "project/create_profile_form.html"

    def get_context_data(self, **kwargs):
        """Provide context for both UserCreationForm and CreateProfileForm."""
        create_form = UserCreationForm  # Create a new instance of the UserCreationForm
        # Get the context from the parent class (CreateView)
        context = super().get_context_data(**kwargs)
        # Add the UserCreationForm instance to the context so it can be rendered in the template
        context['create_form'] = create_form  
        return context

    def form_valid(self, form):
        """Handle submission of both forms together."""
        print(f'CreateProfileView.form_valid(): form.cleaned_data={form.cleaned_data}')
        
        # Create a new UserCreationForm instance and save it to create a new user
        user_form = UserCreationForm(self.request.POST)
        user = user_form.save()

        # Associate the newly created user with the profile form instance
        form.instance.user = user
        
        # Log the user in immediately after creating the user profile
        login(self.request, user)

        # Call the parent class's form_valid method to save the profile form and return a response
        return super().form_valid(form)


# View to show all UserProfiles
class ShowAllUserProfileViews(ListView):
    '''The view to show all Profiles'''

    # Model to query UserProfile instances
    model = UserProfile
    # Template used to display all profiles
    template_name = 'project/show_all_profiles.html'
    # Name of the context variable to hold all profiles in the template
    context_object_name = 'profiles'


# View to show an individual user's profile page
class ShowUserProfilePageView(DetailView):
    '''The view for showing a detailed profile page of a specific user.'''

    # Model to query the UserProfile instance
    model = UserProfile
    # Template used to display the user's profile
    template_name = 'project/show_profile.html'
    # Context variable name for the UserProfile object
    context_object_name = 'profile'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        '''Add additional context data (like receipts, friends, and pending requests) to the profile page.'''
        # Call the parent class method to get the default context
        context = super().get_context_data(**kwargs)
        
        # Get the profile from the context and add related data
        profile = context['profile']
        context['receipts'] = profile.get_receipts()  # Add receipts related to this profile
        context['friends'] = profile.get_friends()  # Add a list of friends of this profile
        context['pending_requests'] = profile.get_pending_friends()  # Add pending friend requests

        return context


# View to show a detailed receipt page
class ShowReceiptPageView(DetailView):
    '''The view to display an individual receipt.'''

    # Model to query the Receipt instance
    model = Receipt
    # Template used to display the receipt
    template_name = 'project/show_receipt.html'
    # Context variable name for the Receipt object
    context_object_name = 'receipt'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        '''Add profile context to the receipt page.'''
        # Call the parent class method to get the default context
        context = super().get_context_data(**kwargs)
        
        # Get the UserProfile for the current user and add it to the context
        profile = UserProfile.objects.get(user=self.request.user)
        context['profile'] = profile

        return context


# View to update the user profile
class UpdateUserProfileForm(LoginRequiredMixin, UpdateView):
    '''The view to update an existing user profile.'''

    # Model to update the UserProfile
    model = UserProfile
    # Form class used for updating the profile
    form_class = UpdateUserProfileForm
    # Template used to render the update profile form
    template_name = 'project/update_user_profile_form.html'
    # Context variable name for the profile being updated
    context_object_name = 'profile'

    def get_login_url(self) -> str:
        '''Return the URL of the login page.'''
        return reverse('login')


# View to accept a pending friend request
class AcceptFriendView(View):
    '''The view to accept a pending friend request.'''

    def dispatch(self, request, *args, **kwargs):
        '''Handle the acceptance of a friend request.'''
        # Get the primary keys (pk) from URL parameters
        pk = kwargs['pk']
        other_pk = kwargs['friend_pk']
        
        # Fetch the profiles of the current user and the friend who sent the request
        profile = UserProfile.objects.get(pk=pk)
        pending_friend = UserProfile.objects.get(pk=other_pk)
        
        # Call the method to accept the pending friendship
        profile.accept_friend(pending_friend)
        
        # Redirect the user to the profile page after accepting the friend request
        return redirect('show_profile', pk=pk)


# View to reject a pending friend request
class RejectFriendView(View):
    '''The view to reject a pending friend request.'''

    def dispatch(self, request, *args, **kwargs):
        '''Handle the rejection of a friend request.'''
        # Get the primary keys (pk) from URL parameters
        pk = kwargs['pk']
        other_pk = kwargs['friend_pk']
        
        # Fetch the profiles of the current user and the friend who sent the request
        profile = UserProfile.objects.get(pk=pk)
        pending_friend = UserProfile.objects.get(pk=other_pk)
        
        # Call the method to reject the pending friendship
        profile.reject_friend(pending_friend)
        
        # Redirect the user to the profile page after rejecting the friend request
        return redirect('show_profile', pk=pk)

class ShowFeedView(DetailView):
    '''The view to display the user's news feed based on their profile.'''

    # Model to query UserProfile instances
    model = UserProfile
    # Template used to display the feed
    template_name = 'project/feed.html'
    # Context variable name for the UserProfile object
    context_object_name = 'profile'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        '''Add the user's feed data to the context.'''
        # Call the parent class method to get the default context
        context = super().get_context_data(**kwargs)
        
        # Get the profile of the current user
        profile = self.object  # The Profile instance from the URL
        
        # Add the feed to the context by calling the get_feed method on the profile
        context['feed'] = profile.get_feed()  # Call the get_news_feed method
        
        return context

    def get_object(self):
        '''Return the profile of the currently logged-in user.'''
        all_profiles = UserProfile.objects.all()
        profile = all_profiles.get(user=self.request.user)  # Fetch the profile based on the logged-in user
        return profile


class ShowFriendSuggestionsView(DetailView):
    '''The view to show friend suggestions for the user.'''

    # Model to query UserProfile instances
    model = UserProfile
    # Template used to display friend suggestions
    template_name = 'project/friend_suggestions.html'
    # Context variable name for the UserProfile object
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        '''Add the list of friend suggestions to the context.'''
        # Call the parent class method to get the default context
        context = super().get_context_data(**kwargs)
        
        # Add the friend suggestions to the context by calling the get_friend_suggestions method on the profile
        context['suggestions'] = self.object.get_friend_suggestions()
        
        return context

    def get_object(self):
        '''Return the profile of the currently logged-in user.'''
        all_profiles = UserProfile.objects.all()
        profile = all_profiles.get(user=self.request.user)  # Fetch the profile based on the logged-in user
        return profile


class AddFriendView(View):
    '''The view to add a friend by sending a friend request.'''

    def dispatch(self, request, *args, **kwargs):
        '''Handle the friend request logic.'''
        # Extract the primary keys (pk) of the profiles from URL parameters
        pk = kwargs['pk']
        other_pk = kwargs['other_pk']
        
        # Fetch the profiles of both the user and the other person
        profile = UserProfile.objects.get(pk=pk)
        other_profile = UserProfile.objects.get(pk=other_pk)
        
        # Add the other user as a friend (this will create a pending friendship)
        profile.add_friend(other_profile)
        
        # Redirect back to the current user's profile page
        return redirect('show_profile', pk=pk)

    def get_login_url(self):
        '''Return the URL for the login page if the user is not authenticated.'''
        return reverse("login")


class UploadReceiptView(LoginRequiredMixin, CreateView):
    '''The view for uploading a receipt image and parsing its data.'''

    # Model to create a new Receipt instance
    model = Receipt
    # Form class used to upload the receipt
    form_class = ReceiptUploadForm
    # Template used for the receipt upload form
    template_name = 'project/upload_receipt.html'

    def get_success_url(self):
        '''Redirect to the user's profile page after a successful upload.'''
        # After the form is saved, redirect to the user's profile page
        profile = self.get_object()
        return reverse('show_profile', kwargs={'pk': profile.pk})

    def get_login_url(self) -> str:
        '''Return the login URL if the user is not authenticated.'''
        return reverse('login')

    def encode_image(self, image_file):
        '''Encode the uploaded image to base64 format for API processing.'''
        return base64.b64encode(image_file.read()).decode('utf-8')

    def get_object(self):
        '''Return the profile of the currently logged-in user.'''
        all_profiles = UserProfile.objects.all()
        profile = all_profiles.get(user=self.request.user)  # Fetch the profile based on the logged-in user
        return profile

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        '''Add the user's profile to the context for rendering the form.'''
        # Call the parent class method to get the default context
        context = super().get_context_data(**kwargs)
        
        # Add the current user's profile to the context
        context['profile'] = self.get_object()
        
        return context

    def form_valid(self, form):
        """
        Handle the receipt image upload, parse the receipt, and save to the database.
        """
        profile = self.get_object()  # Get the current user's profile
        
        # The form has been validated, and the image file is ready to be processed
        receipt_image = form.cleaned_data['receipt_image']
        
        # Step 1: Convert the image to base64
        receipt_base64 = self.encode_image(receipt_image)
    
        # Step 2: Send the image to OpenAI API (or another API) for receipt parsing
        parsed_receipt_data = self.openai_parse_receipt(receipt_base64)
        
        # Step 3: Clean the OpenAI API Response to extract useful data
        receipt_data = self.clean_receipt(parsed_receipt_data)
        
        # Step 4: Save the receipt object (without committing yet) and set related data
        receipt = form.save(commit=False)
        receipt.profile = profile
        receipt.receipt_data = receipt_data
        receipt.total_spent = receipt_data.get('total_amount_spent', None)
        receipt.save()

        # Step 5: Create Item entries for each item in the parsed receipt
        items = receipt_data.get('items', [])
        for item_data in items:
            Item.objects.create(
                receipt=receipt,
                name=item_data.get('name', ''),
                category=item_data.get('category', 'misc'),
                quantity=item_data.get('quantity', 1),
                price=item_data.get('price', 0),
            )
        
        # Redirect to the user's profile page after the receipt is saved
        return redirect('show_profile', pk=profile.pk)

    def form_invalid(self, form):
        """
        Handle the case when the form is invalid.
        """
        # Add any custom error handling or logging if needed
        return super().form_invalid(form)

    def openai_parse_receipt(self, base64_receipt):
        '''Send the base64-encoded receipt image to OpenAI API for parsing.'''
        client = OpenAI()  # Initialize OpenAI client
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Specify the model for parsing
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": "Parse the following receipt text and output the information in a structured JSON format. The keys are store_name, items, and total_amount_spent. Items should be a list of objects, where the keys are name, category, quantity, and price. Categories include Fruits, Vegetables, Grains, Protein, Dairy, and misc. For any fields that you are unable to parse, simply have it as None",
                        },
                        {
                        "type": "image_url",
                        "image_url": {
                            "url":  f"data:image/jpeg;base64,{base64_receipt}"
                        },
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content  # Return the parsed response

    def clean_receipt(self, openai_response):
        '''Clean and parse the OpenAI API response to extract receipt data.'''
        stripped_response = openai_response.replace('```json', '').replace('```','').strip()
        receipt_data = json.loads(stripped_response)  # Parse the cleaned response as JSON
        return receipt_data


class DeleteReceiptPageView(LoginRequiredMixin, DeleteView):
    '''The view to delete a receipt.'''

    # Model for deleting a Receipt instance
    model = Receipt
    # Template used for confirming receipt deletion
    template_name = 'project/delete_receipt_form.html'
    # Context variable name for the Receipt object
    context_object_name = 'receipt'

    def get_login_url(self):
        '''Return the login URL if the user is not authenticated.'''
        return reverse("login")

    def get_success_url(self) -> str:
        '''Redirect to the user's profile page after successful deletion.'''
        # After deletion, redirect to the user's profile page
        receipt = self.get_object()
        return reverse('show_profile', kwargs={'pk': receipt.profile.pk})

class ProfileItemsView(ListView):
    '''View to display all the items that a user has purchased with filtering capabilities'''
    model = Item 
    template_name = "project/show_items.html"
    context_object_name = "items"
    paginate_by = 10
    def get_queryset(self) -> QuerySet[Any]:
        '''Enable filtering'''
        profile = UserProfile.objects.get(user = self.request.user)
        queryset =  Item.objects.filter(receipt__profile = profile)
        # Filter by category (if passed in GET request)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filter by date range (if passed in GET request)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(receipt__date_uploaded__gte=datetime.datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            queryset = queryset.filter(receipt__date_uploaded__lte=datetime.datetime.strptime(date_to, '%Y-%m-%d'))

        # Filter by price (low to high, if passed in GET request)
        price_order = self.request.GET.get('price')
        if price_order == 'low_to_high':
            queryset = queryset.order_by('price')
        elif price_order == 'high_to_low':
            queryset = queryset.order_by('-price')

        return queryset
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = UserProfile.objects.get(user = self.request.user)
                # For the category filter, let's pass the list of possible categories to the template
        context['categories'] = ['Fruits', 'Vegetables', 'Grains', 'Protein', 'Dairy', 'misc']  # Example categories
        context['current_category'] = self.request.GET.get('category', '')
        return context
    
class ShoppingAnalyticsView(View):
    '''View for displaying user analytics'''
    def get(self, request, *args, **kwargs):
        # Get the current user's profile
        profile = UserProfile.objects.get(user=request.user)

        # Prepare the filters for the main items query
        filters = Q(receipt__profile=profile)
        # Query user items data
        items = Item.objects.filter(filters)
        
        # Initialize graph variables
        graph_spending_over_time = None
        graph_category_comparison = None
        graph_store_distribution = None
        
        # Graph 1: Spending Over Time
        if items.exists():  # Check if there are any items for the user
            user_data = list(items.values('receipt__date_uploaded').annotate(
                total_spent=Sum(F('price') * F('quantity'))).order_by('receipt__date_uploaded'))

            # Convert the query set to a pandas DataFrame
            user_df = pd.DataFrame(user_data)

            if not user_df.empty:  # Ensure the DataFrame has data
                # Convert the 'receipt__date_uploaded' column to datetime
                user_df['date'] = pd.to_datetime(user_df['receipt__date_uploaded'])

                # Group by date and sum total spent
                user_df = user_df.groupby('date')['total_spent'].sum().reset_index()

                # Create the line chart with markers (dots)
                fig_spending_over_time = px.line(user_df, x='date', y='total_spent', 
                                                title="User's Spending Over Time", labels={'total_spent': 'Total Spending'})

                # Update the plot to include both lines and markers
                fig_spending_over_time.update_traces(mode='lines+markers')

                # Optional: Update the layout for better clarity and presentation
                fig_spending_over_time.update_layout(
                    showlegend=False,
                    xaxis=dict(
                        title="Date",  # Set the title for x-axis
                        rangeslider=None,  # Disable the range slider
                        fixedrange=True,  # Prevent zooming/scrolling
                        tickformat="%Y-%m-%d",  # Format the ticks for the x-axis
                        tickangle=45,  # Rotate the date labels to avoid overlap
                        showgrid=True,  # Show grid lines for clarity
                        type="category",  # Treat the date as categorical data if it's dense
                    ),
                    yaxis=dict(
                        title="Total Spending",
                    ),
                    margin=dict(l=40, r=40, t=40, b=100)  # Adjust margins to accommodate rotated date labels
                )

                # Convert the Plotly graph to HTML
                graph_spending_over_time = fig_spending_over_time.to_html(full_html=False)

        # Graph 2: Category Spending Comparison
        if items.exists():  # Check if there are any items for the user
            category_data = list(items.values('category').annotate(
                total_spent=Sum(F('price') * F('quantity'))).order_by('category'))
            
            category_df = pd.DataFrame(category_data)

            if not category_df.empty:  # Ensure the DataFrame has data
                fig_category_comparison = px.bar(category_df, x='category', y='total_spent', 
                                                title="Spending by Category", labels={'total_spent': 'Total Spending'})

                # Convert the Plotly graph to HTML
                graph_category_comparison = fig_category_comparison.to_html(full_html=False)

        # Graph 3: Store Spending Distribution
        if items.exists():  # Check if there are any items for the user
            store_data = list(items.values('receipt__receipt_data__store_name').annotate(
                total_spent=Sum(F('price') * F('quantity'))).order_by('receipt__receipt_data__store_name'))
            
            store_df = pd.DataFrame(store_data)

            if not store_df.empty:  # Ensure the DataFrame has data
                fig_store_distribution = px.pie(store_df, names='receipt__receipt_data__store_name', 
                                                values='total_spent', title="Store Spending Distribution")

                # Convert the Plotly graph to HTML
                graph_store_distribution = fig_store_distribution.to_html(full_html=False)

        # Render the template with graphs (or None if no data is available)
        return render(request, 'project/shopping_analytics.html', {
            'graph_spending_over_time': graph_spending_over_time,
            'graph_category_comparison': graph_category_comparison,
            'graph_store_distribution': graph_store_distribution,
            'profile': profile
        })
class LeaderboardView(View):
    '''View for displaying user's analytics against their friends'''
    def get(self, request, *args, **kwargs):
        # Get the current user's profile
        profile = UserProfile.objects.get(user=request.user)
        
        # Get friends of the current user
        friends = profile.get_friends()

        # Get a list of all users to compare (the current user + their friends)
        users_to_compare = [profile] + list(friends)

        # Create a list to store leaderboard data
        leaderboard_data = []

        for user in users_to_compare:
            # Get the user's items (excluding receipts from other profiles)
            items = Item.objects.filter(receipt__profile=user)

            # Aggregate metrics for each user
            stores_shopped_from = items.values('receipt__receipt_data__store_name').distinct().count()
            total_quantity_bought = items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
            total_categories_bought = items.values('category').distinct().count()

            leaderboard_data.append({
                'username': user.email,
                'stores_shopped_from': stores_shopped_from,
                'total_quantity_bought': total_quantity_bought,
                'total_categories_bought': total_categories_bought,
            })

        # Sort the leaderboard data by total quantity bought (or other metric)
        leaderboard_data.sort(key=lambda x: x['total_quantity_bought'], reverse=True)

        # Create a DataFrame for graphing (using Plotly)
        leaderboard_df = pd.DataFrame(leaderboard_data)

        # Create visual comparisons using Plotly

        # Graph 1: Comparison of Total Quantity Bought
        fig_quantity_comparison = px.bar(leaderboard_df, x='username', y='total_quantity_bought', 
                                        title="Total Quantity Bought Comparison", 
                                        labels={'total_quantity_bought': 'Total Quantity Bought'})

        # Graph 2: Comparison of Stores Shopped From
        fig_stores_comparison = px.bar(leaderboard_df, x='username', y='stores_shopped_from', 
                                       title="Stores Shopped From Comparison", 
                                       labels={'stores_shopped_from': 'Stores Shopped From'})

        # Graph 3: Comparison of Categories Bought
        fig_categories_comparison = px.bar(leaderboard_df, x='username', y='total_categories_bought', 
                                           title="Categories Bought Comparison", 
                                           labels={'total_categories_bought': 'Total Categories Bought'})

        # Create a comparison graph for specific categories (e.g., Dairy, Protein)
        # Step 1: Aggregate total quantity for each category for the user and their friends
        category_comparison_data = []
        categories = ['Dairy', 'Protein', 'Vegetables', 'Fruits', 'Grains', 'misc']  # Add more categories as needed
        for user in users_to_compare:
            # Get the user's items filtered by category
            items = Item.objects.filter(receipt__profile=user, category__in=categories)

            # Calculate the total quantity bought for each category
            category_totals = {category: 0 for category in categories}  # Initialize totals for each category
            for category in categories:
                total_quantity = items.filter(category=category).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
                category_totals[category] = total_quantity

            # Append the data for the current user
            category_comparison_data.append({
                'username': user.email,
                **category_totals
            })

        # Step 2: Create a DataFrame for category comparison
        category_comparison_df = pd.DataFrame(category_comparison_data)

        # Step 3: Create a bar chart for category comparison
        fig_category_comparison = px.bar(category_comparison_df, 
                                         x='username', 
                                         y=categories,
                                         title="Category Comparison",
                                         labels={category: f"Total {category} Bought" for category in categories})

        # Convert the Plotly graphs to HTML for embedding in the template
        graph_quantity_comparison = fig_quantity_comparison.to_html(full_html=False)
        graph_stores_comparison = fig_stores_comparison.to_html(full_html=False)
        graph_categories_comparison = fig_categories_comparison.to_html(full_html=False)
        graph_category_comparison = fig_category_comparison.to_html(full_html=False)

        # Render the template with graphs
        return render(request, 'project/leaderboard.html', {
            'profile': profile,
            'leaderboard_data': leaderboard_data,
            'graph_quantity_comparison': graph_quantity_comparison,
            'graph_stores_comparison': graph_stores_comparison,
            'graph_categories_comparison': graph_categories_comparison,
            'graph_category_comparison': graph_category_comparison,
        })