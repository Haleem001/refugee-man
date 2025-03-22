from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Refugee URLs
    path('refugee/create/', views.create_refugee_profile, name='create_refugee_profile'),
    path('refugees/', views.RefugeeListView.as_view(), name='refugee_list'),
    path('refugee/<int:pk>/', views.RefugeeDetailView.as_view(), name='refugee_detail'),
    path('refugee/<int:pk>/update/', views.RefugeeUpdateView.as_view(), name='refugee_update'),
    
    # Housing URLs
    path('housing/', views.HousingListView.as_view(), name='housing_list'),
    path('housing/<int:pk>/', views.HousingDetailView.as_view(), name='housing_detail'),
    path('housing/create/', views.HousingCreateView.as_view(), name='housing_create'),
    path('housing/<int:pk>/update/', views.HousingUpdateView.as_view(), name='housing_update'),
    path('housing/<int:pk>/delete/', views.HousingDeleteView.as_view(), name='housing_delete'),
    
    # Job URLs
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('job/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('job/create/', views.JobCreateView.as_view(), name='job_create'),
    path('job/<int:pk>/update/', views.JobUpdateView.as_view(), name='job_update'),
    path('job/<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    path('job/<int:job_id>/apply/', views.apply_for_job, name='apply_for_job'),
    
    
    # Job Application URLs
    path('applications/', views.JobApplicationListView.as_view(), name='job_application_list'),
]
