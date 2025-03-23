from django.urls import path
from . import views

urlpatterns = [
    # Landing page as home
    path('', views.landing_page, name='home'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile URLs
    path('refugees/create/', views.create_refugee_profile, name='create_refugee_profile'),
    path('ngo/create/', views.create_ngo_profile, name='create_ngo_profile'),
    path('ngo/<int:pk>/update/', views.NGOUpdateView.as_view(), name='ngo_update'),
    
    # Refugee URLs
    path('refugees/', views.RefugeeListView.as_view(), name='refugee_list'),
    path('refugees/<int:pk>/', views.RefugeeDetailView.as_view(), name='refugee_detail'),
    path('refugees/<int:pk>/update/', views.RefugeeUpdateView.as_view(), name='refugee_update'),
    path('refugees/<int:pk>/delete/', views.RefugeeDeleteView.as_view(), name='refugee_delete'),
    
    # Housing URLs
    path('housing/', views.HousingListView.as_view(), name='housing_list'),
    path('housing/create/', views.HousingCreateView.as_view(), name='housing_create'),
    path('housing/<int:pk>/', views.HousingDetailView.as_view(), name='housing_detail'),
    path('housing/<int:pk>/update/', views.HousingUpdateView.as_view(), name='housing_update'),
    path('housing/<int:pk>/delete/', views.HousingDeleteView.as_view(), name='housing_delete'),
    path('housing/<int:pk>/apply/', views.apply_for_housing, name='apply_for_housing'),
    
    # Job URLs
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('jobs/create/', views.JobCreateView.as_view(), name='job_create'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('jobs/<int:pk>/update/', views.JobUpdateView.as_view(), name='job_update'),
    path('jobs/<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    path('jobs/<int:pk>/apply/', views.apply_for_job, name='apply_for_job'),
    
    # Application URLs
    path('applications/housing/', views.HousingApplicationListView.as_view(), name='housing_application_list'),
    path('applications/jobs/', views.JobApplicationListView.as_view(), name='job_application_list'),
    path('applications/housing/<int:pk>/<str:status>/', views.update_housing_application_status, name='update_housing_application_status'),
    path('applications/jobs/<int:pk>/<str:status>/', views.update_job_application_status, name='update_job_application_status'),
]
