from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Refugee, Housing, Job, JobApplication, HousingApplication, NGO

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'user_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})
        self.fields['user_type'].widget.attrs.update({'class': 'form-select'})
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class RefugeeForm(forms.ModelForm):
    class Meta:
        model = Refugee
        fields = [
            'date_of_birth',
            'gender',
            'family_size',
            'country_of_origin',
            'native_language',
            'education_level',
            'skills',
            'medical_conditions',
            'emergency_contact',
            'documents',
            'status'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'family_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of family members',
                'min': '1'
            }),
            'country_of_origin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country of origin'
            }),
            'native_language': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Native language'
            }),
            'education_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Highest level of education'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'List your skills and qualifications',
                'rows': 4
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'List any medical conditions (if any)',
                'rows': 3
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact information'
            }),
            'documents': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-select'})
        }

class HousingForm(forms.ModelForm):
    class Meta:
        model = Housing
        fields = [
            'name',
            'description',
            'location',
            'address',
            'capacity',
            'current_occupancy',
            'housing_type',
            'amenities',
            'status',
            'cost_per_month'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Housing name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detailed description of the housing',
                'rows': 4
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'General location (e.g., city, district)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Full address',
                'rows': 3
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum capacity',
                'min': '1'
            }),
            'current_occupancy': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Current number of occupants',
                'min': '0'
            }),
            'housing_type': forms.Select(attrs={'class': 'form-select'}),
            'amenities': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'List available amenities',
                'rows': 3
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'cost_per_month': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Monthly cost (if applicable)',
                'min': '0',
                'step': '0.01'
            })
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title',
            'description',
            'location',
            'employer',
            'job_type',
            'salary_range',
            'requirements',
            'benefits',
            'deadline',
            'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Job description',
                'rows': 4
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job location'
            }),
            'employer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Employer name'
            }),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'salary_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Salary range (e.g., $40,000 - $50,000)'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Job requirements and qualifications',
                'rows': 4
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Job benefits and perks',
                'rows': 3
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your cover letter here',
                'rows': 6
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

class HousingApplicationForm(forms.ModelForm):
    class Meta:
        model = HousingApplication
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Please provide any additional information that might help with your application...'
            }),
        }

class NGOProfileForm(forms.ModelForm):
    class Meta:
        model = NGO
        fields = [
            'organization_name',
            'registration_number',
            'description',
            'website',
            'contact_email',
            'contact_phone',
            'address',
            'areas_of_focus',
            'established_date'
        ]
        widgets = {
            'organization_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Organization name'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Registration number'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of your organization',
                'rows': 4
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.org'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@organization.org'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Organization address',
                'rows': 3
            }),
            'areas_of_focus': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'List your main areas of focus',
                'rows': 4
            }),
            'established_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
