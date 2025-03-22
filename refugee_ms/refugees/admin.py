from django.contrib import admin
from .models import CustomUser, Refugee, Housing, Job, JobApplication, HousingApplication


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(Refugee)
class RefugeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'country_of_origin', 'family_size', 'registered_at', 'status')
    list_filter = ('country_of_origin', 'status')
    search_fields = ('user__username', 'user__email', 'country_of_origin')

@admin.register(Housing)
class HousingAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'housing_type', 'capacity', 'current_occupancy', 'status')
    list_filter = ('housing_type', 'status')
    search_fields = ('name', 'location')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'job_type', 'posted_at', 'deadline', 'is_active')
    list_filter = ('job_type', 'is_active')
    search_fields = ('title', 'employer', 'location')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('refugee', 'job', 'status', 'applied_at', 'last_updated')
    list_filter = ('status', 'applied_at')
    search_fields = ('refugee__user__username', 'job__title')

@admin.register(HousingApplication)
class HousingApplicationAdmin(admin.ModelAdmin):
    list_display = ('refugee', 'housing', 'status', 'application_date', 'decision_date')
    list_filter = ('status', 'application_date')
    search_fields = ('refugee__user__username', 'housing__name')
