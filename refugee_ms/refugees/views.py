from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import Refugee, Housing, Job, JobApplication, CustomUser, HousingApplication
from .forms import RefugeeForm, HousingForm, JobForm, JobApplicationForm, CustomUserCreationForm

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.user_type == 'refugee':
                return redirect('create_refugee_profile')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'refugees/register.html', {'form': form})

@login_required
def dashboard(request):
    context = {}
    
    # Basic statistics
    context['total_refugees'] = Refugee.objects.count()
    context['available_housing'] = Housing.objects.filter(status='available').count()
    context['active_jobs'] = Job.objects.filter(is_active=True, deadline__gt=timezone.now()).count()
    context['pending_applications'] = JobApplication.objects.filter(status='pending').count()

    # Demographics data
    demographics = Refugee.objects.values('country_of_origin').annotate(count=Count('id'))
    context['demographics_labels'] = json.dumps([d['country_of_origin'] for d in demographics])
    context['demographics_data'] = json.dumps([d['count'] for d in demographics])

    # Housing data
    housing_types = Housing.objects.values('housing_type').annotate(
        occupied=Count('id', filter=Q(status='occupied')),
        available=Count('id', filter=Q(status='available'))
    )
    context['housing_labels'] = json.dumps([h['housing_type'] for h in housing_types])
    context['housing_occupied_data'] = json.dumps([h['occupied'] for h in housing_types])
    context['housing_available_data'] = json.dumps([h['available'] for h in housing_types])

    # Recent activities
    recent_activities = []
    
    # Recent refugee registrations
    recent_refugees = Refugee.objects.order_by('-registered_at')[:5]
    for refugee in recent_refugees:
        recent_activities.append({
            'title': 'New Refugee Registration',
            'description': f'{refugee.user.get_full_name()} from {refugee.country_of_origin}',
            'timestamp': refugee.registered_at
        })

    # Recent job applications
    recent_job_apps = JobApplication.objects.order_by('-applied_at')[:5]
    for app in recent_job_apps:
        recent_activities.append({
            'title': 'New Job Application',
            'description': f'{app.refugee.user.get_full_name()} applied for {app.job.title}',
            'timestamp': app.applied_at
        })

    # Recent housing applications
    recent_housing_apps = HousingApplication.objects.order_by('-application_date')[:5]
    for app in recent_housing_apps:
        recent_activities.append({
            'title': 'New Housing Application',
            'description': f'{app.refugee.user.get_full_name()} applied for {app.housing.name}',
            'timestamp': app.application_date
        })

    # Sort activities by timestamp and get the 10 most recent
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    context['recent_activities'] = recent_activities[:10]

    # Upcoming events (job deadlines and housing availability)
    upcoming_events = []
    
    # Upcoming job deadlines
    upcoming_jobs = Job.objects.filter(
        deadline__gt=timezone.now(),
        deadline__lte=timezone.now() + timedelta(days=7)
    ).order_by('deadline')[:5]
    
    for job in upcoming_jobs:
        upcoming_events.append({
            'title': f'Job Deadline: {job.title}',
            'description': f'Application deadline for {job.employer}',
            'date': job.deadline,
            'location': job.location
        })

    # Upcoming housing availability
    upcoming_housing = Housing.objects.filter(
        status='maintenance'
    ).order_by('last_updated')[:5]
    
    for housing in upcoming_housing:
        upcoming_events.append({
            'title': f'Housing Available Soon: {housing.name}',
            'description': f'{housing.get_housing_type_display()} will be available',
            'date': housing.last_updated + timedelta(days=7),
            'location': housing.location
        })

    # Sort events by date
    upcoming_events.sort(key=lambda x: x['date'])
    context['upcoming_events'] = upcoming_events

    return render(request, 'refugees/dashboard.html', context)

# Refugee Views
@login_required
def create_refugee_profile(request):
    if hasattr(request.user, 'refugee'):
        messages.warning(request, 'You already have a refugee profile.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RefugeeForm(request.POST)
        if form.is_valid():
            refugee = form.save(commit=False)
            refugee.user = request.user
            refugee.save()
            messages.success(request, 'Refugee profile created successfully!')
            return redirect('dashboard')
    else:
        form = RefugeeForm()
    
    return render(request, 'refugees/refugee_form.html', {'form': form})

class RefugeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Refugee
    template_name = 'refugees/refugee_list.html'
    context_object_name = 'refugees'
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo']

class RefugeeDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Refugee
    template_name = 'refugees/refugee_detail.html'
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo'] or self.get_object().user == self.request.user

# Housing Views
class HousingListView(ListView):
    model = Housing
    template_name = 'refugees/housing_list.html'
    context_object_name = 'housings'

class HousingDetailView(DetailView):
    model = Housing
    template_name = 'refugees/housing_detail.html'

class HousingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Housing
    form_class = HousingForm
    template_name = 'refugees/housing_form.html'
    success_url = reverse_lazy('housing_list')
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo']

class HousingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Housing
    form_class = HousingForm
    template_name = 'refugees/housing_form.html'
    success_url = reverse_lazy('housing_list')
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo']

class HousingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Housing
    template_name = 'refugees/housing_confirm_delete.html'
    success_url = reverse_lazy('housing_list')
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo']

# Job Views
class JobListView(ListView):
    model = Job
    template_name = 'refugees/job_list.html'
    context_object_name = 'jobs'

class JobDetailView(DetailView):
    model = Job
    template_name = 'refugees/job_detail.html'

class JobCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'refugees/job_form.html'
    success_url = reverse_lazy('job_list')
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo']

class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'refugees/job_form.html'
    success_url = reverse_lazy('job_list')
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo']

class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    template_name = 'refugees/job_confirm_delete.html'
    success_url = reverse_lazy('job_list')
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo']

# Job Application Views
@login_required
def apply_for_job(request, job_id):
    if request.user.user_type != 'refugee':
        messages.error(request, 'Only refugees can apply for jobs.')
        return redirect('job_list')
    
    try:
        refugee = request.user.refugee
    except Refugee.DoesNotExist:
        messages.error(request, 'Please complete your refugee profile first.')
        return redirect('create_refugee_profile')
    
    job = get_object_or_404(Job, id=job_id)
    
    # Check if already applied
    if JobApplication.objects.filter(refugee=refugee, job=job).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=job_id)
    
    # Create application
    JobApplication.objects.create(refugee=refugee, job=job)
    messages.success(request, f'Successfully applied for {job.title}!')
    return redirect('job_detail', pk=job_id)

class JobApplicationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = JobApplication
    template_name = 'refugees/job_application_list.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        if self.request.user.user_type == 'refugee':
            return JobApplication.objects.filter(refugee=self.request.user.refugee)
        return JobApplication.objects.all()
    
    def test_func(self):
        return True  # Everyone can see their own applications

# Add these to your existing views.py file

class RefugeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Refugee
    form_class = RefugeeForm
    template_name = 'refugees/refugee_form.html'
    success_url = reverse_lazy('dashboard')
    
    def test_func(self):
        refugee = self.get_object()
        return self.request.user.user_type == 'admin' or refugee.user == self.request.user
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')
