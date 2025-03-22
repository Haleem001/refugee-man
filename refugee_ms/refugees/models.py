from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('refugee', 'Refugee'),
        ('admin', 'Admin'),
        ('ngo', 'NGO'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=100, blank=True, help_text="Organization name for NGO users")

class Refugee(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    family_size = models.IntegerField(validators=[MinValueValidator(1)])
    country_of_origin = models.CharField(max_length=100)
    native_language = models.CharField(max_length=50)
    education_level = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    documents = models.FileField(upload_to='refugee_documents/', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    registered_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} from {self.country_of_origin}"

class Housing(models.Model):
    HOUSING_TYPE_CHOICES = [
        ('camp', 'Refugee Camp'),
        ('private', 'Private Home'),
        ('apartment', 'Apartment'),
        ('shelter', 'Temporary Shelter'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    address = models.TextField()
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    current_occupancy = models.IntegerField(default=0)
    housing_type = models.CharField(max_length=10, choices=HOUSING_TYPE_CHOICES)
    amenities = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    cost_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_housing_type_display()})"

    @property
    def is_available(self):
        return self.status == 'available' and self.current_occupancy < self.capacity

class HousingApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    refugee = models.ForeignKey(Refugee, on_delete=models.CASCADE)
    housing = models.ForeignKey(Housing, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    application_date = models.DateTimeField(auto_now_add=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.refugee.user.get_full_name()} - {self.housing.name}"

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    employer = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    salary_range = models.CharField(max_length=100, blank=True)
    requirements = models.TextField()
    benefits = models.TextField(blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.employer}"

    @property
    def is_expired(self):
        return timezone.now() > self.deadline

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Stage'),
        ('offered', 'Job Offered'),
        ('accepted', 'Offer Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    refugee = models.ForeignKey(Refugee, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='job_applications/', blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.refugee.user.get_full_name()} - {self.job.title}"

    class Meta:
        unique_together = ('refugee', 'job')