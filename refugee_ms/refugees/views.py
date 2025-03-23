from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import Refugee, Housing, Job, JobApplication, CustomUser, HousingApplication, NGO
from .forms import RefugeeForm, HousingForm, JobForm, JobApplicationForm, CustomUserCreationForm, HousingApplicationForm, NGOProfileForm

def landing_page(request):
    """Landing page view that shows different content based on authentication status"""
    return render(request, 'refugees/landing.html')

def login_view(request):
    """Custom login view to handle user authentication"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'refugees/login.html')

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
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if user has a profile (only for refugee and ngo users)
    has_profile = True  # Default to True for admin users
    if request.user.user_type == 'refugee':
        has_profile = hasattr(request.user, 'refugee')
    elif request.user.user_type == 'ngo':
        has_profile = hasattr(request.user, 'ngo')
    
    context = {
        'user_type': request.user.user_type,
        'has_profile': has_profile
    }
    
    # Common statistics for all users
    context.update({
        'total_refugees': Refugee.objects.count(),
        'total_housing': Housing.objects.count(),
        'total_jobs': Job.objects.count(),
        'available_housing_count': Housing.objects.filter(status='available').count(),
        'active_jobs': Job.objects.filter(is_active=True, deadline__gt=timezone.now()).count(),
        'pending_applications': HousingApplication.objects.filter(status='pending').count() + 
                             JobApplication.objects.filter(status='pending').count(),
    })
    
    # Demographics data for charts
    demographics = {
        'labels': ['Male', 'Female', 'Other'],
        'data': [
            Refugee.objects.filter(gender='M').count(),
            Refugee.objects.filter(gender='F').count(),
            Refugee.objects.filter(gender='O').count(),
        ]
    }
    context['demographics_labels'] = json.dumps(demographics['labels'])
    context['demographics_data'] = json.dumps(demographics['data'])
    
    # Housing data for charts
    housing_types = Housing.HOUSING_TYPE_CHOICES
    housing_labels = [type[1] for type in housing_types]
    housing_occupied = []
    housing_available = []
    
    for type_code, _ in housing_types:
        type_housing = Housing.objects.filter(housing_type=type_code)
        housing_occupied.append(type_housing.filter(status='occupied').count())
        housing_available.append(type_housing.filter(status='available').count())
    
    context['housing_labels'] = json.dumps(housing_labels)
    context['housing_occupied_data'] = json.dumps(housing_occupied)
    context['housing_available_data'] = json.dumps(housing_available)
    
    # Recent activities
    recent_activities = []
    
    # Add recent housing applications
    for app in HousingApplication.objects.order_by('-application_date')[:5]:
        recent_activities.append({
            'title': f'Housing Application: {app.housing.name}',
            'description': f'Application from {app.refugee.user.get_full_name()}',
            'timestamp': app.application_date
        })
    
    # Add recent job applications
    for app in JobApplication.objects.order_by('-applied_at')[:5]:
        recent_activities.append({
            'title': f'Job Application: {app.job.title}',
            'description': f'Application from {app.refugee.user.get_full_name()}',
            'timestamp': app.applied_at
        })
    
    # Sort activities by timestamp and take the 5 most recent
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    context['recent_activities'] = recent_activities[:5]
    
    if request.user.user_type == 'refugee':
        try:
            refugee = request.user.refugee
            context.update({
                'refugee': refugee,
                'housing_applications': HousingApplication.objects.filter(refugee=refugee).order_by('-application_date')[:5],
                'job_applications': JobApplication.objects.filter(refugee=refugee).order_by('-applied_at')[:5],
                'available_housing': Housing.objects.filter(status='available').order_by('-created_at')[:5],
                'available_jobs': Job.objects.filter(is_active=True, deadline__gt=timezone.now()).order_by('-posted_at')[:5]
            })
        except AttributeError:
            pass
    elif request.user.user_type == 'ngo':
        try:
            ngo = request.user.ngo
            context.update({
                'ngo': ngo,
                'housing_listings': Housing.objects.filter(ngo=ngo).order_by('-created_at')[:5],
                'job_listings': Job.objects.filter(ngo=ngo).order_by('-posted_at')[:5],
                'housing_applications': HousingApplication.objects.filter(housing__ngo=ngo).order_by('-application_date')[:5],
                'job_applications': JobApplication.objects.filter(job__ngo=ngo).order_by('-applied_at')[:5]
            })
        except AttributeError:
            pass
    elif request.user.user_type == 'admin':
        context.update({
            'total_ngos': NGO.objects.count(),
            'recent_applications': HousingApplication.objects.order_by('-application_date')[:5],
            'recent_job_applications': JobApplication.objects.order_by('-applied_at')[:5]
        })
    
    return render(request, 'refugees/dashboard.html', context)

# Refugee Views
@login_required
def create_ngo_profile(request):
    if request.user.user_type != 'ngo':
        messages.error(request, 'Only NGO users can create NGO profiles.')
        return redirect('dashboard')
    
    if hasattr(request.user, 'ngo'):
        messages.info(request, 'You already have an NGO profile.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = NGOProfileForm(request.POST)
        if form.is_valid():
            ngo_profile = form.save(commit=False)
            ngo_profile.user = request.user
            ngo_profile.save()
            messages.success(request, 'NGO profile created successfully!')
            return redirect('dashboard')
    else:
        form = NGOProfileForm()
    
    return render(request, 'refugees/create_ngo_profile.html', {'form': form})

@login_required
def create_refugee_profile(request):
    if request.user.user_type != 'refugee':
        messages.error(request, 'Only refugee users can create refugee profiles.')
        return redirect('dashboard')
    
    if hasattr(request.user, 'refugee'):
        messages.info(request, 'You already have a refugee profile.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RefugeeForm(request.POST, request.FILES)
        if form.is_valid():
            refugee_profile = form.save(commit=False)
            refugee_profile.user = request.user
            refugee_profile.save()
            messages.success(request, 'Refugee profile created successfully!')
            return redirect('dashboard')
    else:
        form = RefugeeForm()
    
    return render(request, 'refugees/create_refugee_profile.html', {'form': form})

class RefugeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Refugee
    template_name = 'refugees/refugee_list.html'
    context_object_name = 'refugees'
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo']  # Only allow admin and NGO users
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to view the list of refugees.')
        return redirect('dashboard')
    
    def get_queryset(self):
        # For refugees, only show their own profile
        if self.request.user.user_type == 'refugee':
            return Refugee.objects.filter(user=self.request.user)
        else:
            # For NGOs and admins, show all refugees
            return Refugee.objects.all()

class RefugeeDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Refugee
    template_name = 'refugees/refugee_detail.html'
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'ngo'] or self.get_object().user == self.request.user

class RefugeeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Refugee
    template_name = 'refugees/refugee_confirm_delete.html'
    success_url = reverse_lazy('refugee_list')
    
    def test_func(self):
        return self.request.user.user_type == 'admin'
    
    def delete(self, request, *args, **kwargs):
        refugee = self.get_object()
        # Delete the associated user account
        refugee.user.delete()
        messages.success(request, 'Refugee profile and associated account deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Housing Views
class HousingListView(LoginRequiredMixin, ListView):
    model = Housing
    template_name = 'refugees/housing_list.html'
    context_object_name = 'housings'
    
    def get_queryset(self):
        if self.request.user.user_type == 'refugee':
            # Show only available housing for refugees
            return Housing.objects.filter(status='available')
        elif self.request.user.user_type == 'ngo':
            # Show NGO's own listings
            return Housing.objects.filter(ngo=self.request.user.ngo)
        elif self.request.user.user_type == 'admin':
            # Show all housing for admin
            return Housing.objects.all()
        return Housing.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.request.user.user_type
        return context

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
    
    def form_valid(self, form):
        form.instance.ngo = self.request.user.ngo
        return super().form_valid(form)

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
class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'refugees/job_list.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        if self.request.user.user_type == 'refugee':
            # Show only active jobs for refugees
            return Job.objects.filter(is_active=True, deadline__gt=timezone.now())
        elif self.request.user.user_type == 'ngo':
            # Show NGO's own listings
            return Job.objects.filter(ngo=self.request.user.ngo)
        elif self.request.user.user_type == 'admin':
            # Show all jobs for admin
            return Job.objects.all()
        return Job.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.request.user.user_type
        return context

class JobDetailView(DetailView):
    model = Job
    template_name = 'refugees/job_detail.html'

class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'refugees/job_form.html'
    success_url = reverse_lazy('job_list')

    def form_valid(self, form):
        form.instance.ngo = self.request.user.ngo
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'ngo':
            messages.error(request, "Only NGO users can create job listings.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

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
def apply_for_job(request, pk):
    if request.user.user_type != 'refugee':
        messages.error(request, 'Only refugees can apply for jobs.')
        return redirect('job_list')
    
    try:
        refugee = request.user.refugee
    except AttributeError:
        messages.error(request, 'Please complete your refugee profile first.')
        return redirect('create_refugee_profile')
    
    job = get_object_or_404(Job, id=pk)
    
    # Check if already applied
    if JobApplication.objects.filter(refugee=refugee, job=job).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)
    
    # Create application
    JobApplication.objects.create(refugee=refugee, job=job)
    messages.success(request, f'Successfully applied for {job.title}!')
    return redirect('job_detail', pk=pk)

class JobApplicationListView(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = 'refugees/job_application_list.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        if self.request.user.user_type == 'refugee':
            return JobApplication.objects.filter(refugee=self.request.user.refugee)
        elif self.request.user.user_type == 'ngo':
            return JobApplication.objects.filter(job__ngo=self.request.user.ngo)
        elif self.request.user.user_type == 'admin':
            return JobApplication.objects.all()
        return JobApplication.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.request.user.user_type
        return context

# Add these to your existing views.py file

class RefugeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Refugee
    form_class = RefugeeForm
    template_name = 'refugees/refugee_form.html'
    success_url = reverse_lazy('dashboard')
    
    def test_func(self):
        refugee = self.get_object()
        return self.request.user.user_type == 'admin' or refugee.user == self.request.user

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def apply_for_housing(request, pk):
    if request.user.user_type != 'refugee':
        messages.error(request, 'Only refugees can apply for housing.')
        return redirect('housing_list')
    
    try:
        refugee = request.user.refugee
    except Refugee.DoesNotExist:
        messages.error(request, 'Please complete your refugee profile first.')
        return redirect('create_refugee_profile')
    
    housing = get_object_or_404(Housing, pk=pk)
    
    # Check if housing is available
    if housing.status != 'available':
        messages.error(request, 'This housing is not currently available.')
        return redirect('housing_detail', pk=pk)
    
    # Check if already applied
    if HousingApplication.objects.filter(refugee=refugee, housing=housing).exists():
        messages.warning(request, 'You have already applied for this housing.')
        return redirect('housing_detail', pk=pk)
    
    if request.method == 'POST':
        form = HousingApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.refugee = refugee
            application.housing = housing
            application.save()
            messages.success(request, f'Successfully applied for {housing.name}!')
            return redirect('housing_detail', pk=pk)
    else:
        form = HousingApplicationForm()
    
    return render(request, 'refugees/housing_application_form.html', {
        'form': form,
        'housing': housing
    })

class HousingApplicationListView(LoginRequiredMixin, ListView):
    model = HousingApplication
    template_name = 'refugees/housing_application_list.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        if self.request.user.user_type == 'refugee':
            return HousingApplication.objects.filter(refugee=self.request.user.refugee)
        elif self.request.user.user_type == 'ngo':
            return HousingApplication.objects.filter(housing__ngo=self.request.user.ngo)
        elif self.request.user.user_type == 'admin':
            return HousingApplication.objects.all()
        return HousingApplication.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.request.user.user_type
        return context

class NGOUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = NGO
    form_class = NGOProfileForm
    template_name = 'refugees/ngo_form.html'
    success_url = reverse_lazy('dashboard')
    
    def test_func(self):
        ngo = self.get_object()
        return self.request.user.user_type == 'admin' or ngo.user == self.request.user

@login_required
def update_housing_application_status(request, pk, status):
    if request.user.user_type not in ['admin', 'ngo']:
        messages.error(request, 'You do not have permission to update application status.')
        return redirect('dashboard')
    
    application = get_object_or_404(HousingApplication, pk=pk)
    
    # Check if the user has permission to update this application
    if request.user.user_type == 'ngo' and application.housing.ngo != request.user.ngo:
        messages.error(request, 'You can only update applications for your own housing listings.')
        return redirect('housing_application_list')
    
    if status not in ['approved', 'rejected']:
        messages.error(request, 'Invalid status.')
        return redirect('housing_application_list')
    
    application.status = status
    application.save()
    
    if status == 'approved':
        # Update housing status to occupied
        housing = application.housing
        housing.status = 'occupied'
        housing.save()
        messages.success(request, f'Housing application for {application.refugee.user.get_full_name()} has been approved.')
    else:
        messages.success(request, f'Housing application for {application.refugee.user.get_full_name()} has been rejected.')
    
    return redirect('housing_application_list')

@login_required
def update_job_application_status(request, pk, status):
    if request.user.user_type not in ['admin', 'ngo']:
        messages.error(request, 'You do not have permission to update application status.')
        return redirect('dashboard')
    
    application = get_object_or_404(JobApplication, pk=pk)
    
    # Check if the user has permission to update this application
    if request.user.user_type == 'ngo' and application.job.ngo != request.user.ngo:
        messages.error(request, 'You can only update applications for your own job listings.')
        return redirect('job_application_list')
    
    if status not in ['approved', 'rejected']:
        messages.error(request, 'Invalid status.')
        return redirect('job_application_list')
    
    application.status = status
    application.save()
    
    messages.success(request, f'Job application for {application.refugee.user.get_full_name()} has been {status}.')
    return redirect('job_application_list')
