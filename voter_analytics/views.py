# File: views.py
# Author: James Xiao (jamxiao@bu.edu), 10/07/2024
# Description: file to specify the views that will handle requests for mini_fb app.
from typing import Any
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models.functions import Lower
from django.db.models import Min, Max
import plotly.graph_objects as go
from .models import Voter
from .models import * 
from django.db.models import Count
from django.db.models import Q

# Create your views here.
class VoterListView(ListView):
    '''View to show a list of voters'''
    template_name = 'voter_analytics/voters.html'
    model = Voter 
    context_object_name = 'voters'
    paginate_by = 100
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voter_scores'] = range(6)  # Voter scores from 0 to 5
        birth_years = Voter.objects.aggregate(
            min_year=Min('date_of_birth'),
            max_year=Max('date_of_birth')
        )

        # Calculate the range of birth years based on the data
        if birth_years['min_year'] and birth_years['max_year']:
            # Use the year part of the date_of_birth for filtering
            min_year = birth_years['min_year'].year
            max_year = birth_years['max_year'].year
            context['birth_years'] = range(min_year, max_year + 1)
        else:
            # Fallback to default range if no data is found
            context['birth_years'] = range(1900, 2024)  # Example range for years
        context['party_affiliations'] = (
            Voter.objects.order_by()
            .annotate(lower_party=Lower('party_affiliation'))
            .values_list('lower_party', flat=True)
            .distinct()
        )

        # Include existing filters in context to keep form data after submission
        context['party_affiliation'] = self.request.GET.get('party_affiliation', '')
        context['min_dob'] = self.request.GET.get('min_dob', '')
        context['max_dob'] = self.request.GET.get('max_dob', '')
        context['voter_score'] = self.request.GET.get('voter_score', '')
        context['v20state'] = self.request.GET.get('v20state', False)
        context['v21town'] = self.request.GET.get('v21town', False)
        context['v21primary'] = self.request.GET.get('v21primary', False)
        context['v22general'] = self.request.GET.get('v22general', False)
        context['v23town'] = self.request.GET.get('v23town', False)
        return context
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering logic based on GET parameters
        party_affiliation = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')
        
        # Apply filters if they exist
        if party_affiliation:
            queryset = queryset.filter(party_affiliation__icontains=party_affiliation)
        
        if min_dob:
            queryset = queryset.filter(date_of_birth__year__gte=min_dob)
        
        if max_dob:
            queryset = queryset.filter(date_of_birth__year__lte=max_dob)
        
        if voter_score:
            queryset = queryset.filter(voter_score=voter_score)
        
        election_filter = Q()  # Start with an empty Q object
        # Checkboxes for voting participation
        if self.request.GET.get('v20state'):
            election_filter &= Q(v20state=True)
        if self.request.GET.get('v21town'):
            election_filter &= Q(v21town=True)
        if self.request.GET.get('v21primary'):
            election_filter &= Q(v21primary=True)
        if self.request.GET.get('v22general'):
            election_filter &= Q(v22general=True)
        if self.request.GET.get('v23town'):
            election_filter &= Q(v23town=True)
        queryset = queryset.filter(election_filter)
        return queryset
    
class VoterDetailView(DetailView):
    '''View to show a single voter's details'''
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'

class GraphView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get filter criteria from the request
        party_affiliation = self.request.GET.get('party_affiliation', '')
        min_dob = self.request.GET.get('min_dob', '')  # Year (e.g., 1990)
        max_dob = self.request.GET.get('max_dob', '')  # Year (e.g., 2000)
        voter_score = self.request.GET.get('voter_score', '')
        
        # Get selected checkboxes for specific elections
        v20state = self.request.GET.get('v20state', '')
        v21town = self.request.GET.get('v21town', '')
        v21primary = self.request.GET.get('v21primary', '')
        v22general = self.request.GET.get('v22general', '')
        v23town = self.request.GET.get('v23town', '')

        # Aggregate the birth year range for all voters
        birth_years = Voter.objects.aggregate(
            min_year=Min('date_of_birth'),
            max_year=Max('date_of_birth')
        )

        # Calculate the range of birth years based on the data
        if birth_years['min_year'] and birth_years['max_year']:
            min_year = birth_years['min_year'].year
            max_year = birth_years['max_year'].year
            context['birth_years'] = range(min_year, max_year + 1)
        else:
            context['birth_years'] = range(1900, 2024)  # Example range for years

        # Start with all voters
        voters = Voter.objects.all()

        # Apply filters from the request
        if party_affiliation:
            voters = voters.filter(party_affiliation__icontains=party_affiliation)

        # Handle date filters (min_dob and max_dob)
        if min_dob:
            voters = voters.filter(date_of_birth__year__gte=int(min_dob))
        
        if max_dob:
            voters = voters.filter(date_of_birth__year__lte=int(max_dob))
        
        if voter_score:
            voters = voters.filter(voter_score=voter_score)

        election_filter = Q()  # Start with an empty Q object

        if v20state == 'True':
            election_filter &= Q(v20state=True)
        if v21town == 'True':
            election_filter &= Q(v21town=True)
        if v21primary == 'True':
            election_filter &= Q(v21primary=True)
        if v22general == 'True':
            election_filter &= Q(v22general=True)
        if v23town == 'True':
            election_filter &= Q(v23town=True)

        # Apply the combined election filter
        voters = voters.filter(election_filter)
        # Create the graphs
        # 1. Histogram for Voter Birth Year Distribution based on selected checkboxes
        graph_birth_years = voters.values('date_of_birth__year').annotate(count=Count('id')).order_by('date_of_birth__year')
        birth_year_data = [year['date_of_birth__year'] for year in graph_birth_years]
        birth_count_data = [year['count'] for year in graph_birth_years]

        birth_year_chart = go.Figure(data=[go.Bar(
            x=birth_year_data,
            y=birth_count_data,
            marker=dict(color='blue')
        )])
        birth_year_chart.update_layout(title="Voter Birth Year Distribution", xaxis_title="Year", yaxis_title="Count")

        # 2. Pie Chart
        party_affiliations = voters.values('party_affiliation').annotate(count=Count('id'))
        party_labels = [party['party_affiliation'] for party in party_affiliations]
        party_count = [party['count'] for party in party_affiliations]

        party_pie_chart = go.Figure(data=[go.Pie(labels=party_labels, values=party_count)])
        party_pie_chart.update_layout(title="Voter Party Affiliation Distribution")
     
        # Initialize election counts dictionary to hold individual counts for each election
        election_counts = {}

        # Checkboxes for election participation (whether the checkbox is selected)
        if v20state == 'True':
            election_counts['2020 State'] = voters.filter(v20state=True).count()

        if v21town == 'True':
            election_counts['2021 Town'] = voters.filter(v21town=True).count()

        if v21primary == 'True':
            election_counts['2021 Primary'] = voters.filter(v21primary=True).count()

        if v22general == 'True':
            election_counts['2022 General'] = voters.filter(v22general=True).count()

        if v23town == 'True':
            election_counts['2023 Town'] = voters.filter(v23town=True).count()

        # If no elections are selected, include all elections
        if not election_counts:
            election_counts = {
                '2020 State': voters.filter(v20state=True).count(),
                '2021 Town': voters.filter(v21town=True).count(),
                '2021 Primary': voters.filter(v21primary=True).count(),
                '2022 General': voters.filter(v22general=True).count(),
                '2023 Town': voters.filter(v23town=True).count(),
            }

        # Prepare the data for the bar chart
        election_labels = list(election_counts.keys())
        election_counts_values = list(election_counts.values())
        # Create the bar chart for election participation
        election_participation_chart = go.Figure(data=[go.Bar(
            x=election_labels,
            y=election_counts_values,
            marker=dict(color='green')
        )])

        election_participation_chart.update_layout(
            title="Voter Participation in Elections",
            xaxis_title="Election",
            yaxis_title="Count"
        )

        # Add graph divs to the context
        context['birth_year_chart'] = birth_year_chart.to_html(full_html=False)
        context['party_pie_chart'] = party_pie_chart.to_html(full_html=False)
        context['election_participation_chart'] = election_participation_chart.to_html(full_html=False)

        # Add filter data to the context
        context['party_affiliations'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        context['voter_scores'] = Voter.objects.values_list('voter_score', flat=True).distinct()

        return context