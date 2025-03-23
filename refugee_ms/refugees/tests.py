from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Refugee, Housing, Job, JobApplication, HousingApplication, NGO
from .forms import RefugeeForm, HousingForm, JobForm, NGOProfileForm

User = get_user_model()

class RefugeeManagementSystemTests(TestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            user_type='admin'
        )
        self.ngo_user = User.objects.create_user(
            username='ngo',
            password='ngo123',
            user_type='ngo'
        )
        self.refugee_user = User.objects.create_user(
            username='refugee',
            password='refugee123',
            user_type='refugee'
        )
        
        # Create NGO profile
        self.ngo = NGO.objects.create(
            user=self.ngo_user,
            organization_name='Test NGO',
            organization_type='charity',
            location='Test Location',
            contact_number='1234567890'
        )
        
        # Create Refugee profile
        self.refugee = Refugee.objects.create(
            user=self.refugee_user,
            gender='M',
            age=25,
            country_of_origin='Test Country',
            languages='English'
        )
        
        # Create test housing
        self.housing = Housing.objects.create(
            ngo=self.ngo,
            name='Test Housing',
            housing_type='apartment',
            location='Test Location',
            capacity=4,
            description='Test Description',
            status='available'
        )
        
        # Create test job
        self.job = Job.objects.create(
            ngo=self.ngo,
            title='Test Job',
            job_type='full_time',
            location='Test Location',
            description='Test Description',
            posted_at=timezone.now(),
            deadline=timezone.now() + timedelta(days=30),
            is_active=True
        )

    def test_landing_page(self):
        response = self.client.get(reverse('landing_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refugees/landing.html')

    def test_login_view(self):
        # Test successful login
        response = self.client.post(reverse('login'), {
            'username': 'refugee',
            'password': 'refugee123'
        })
        self.assertRedirects(response, reverse('dashboard'))
        
        # Test invalid login
        response = self.client.post(reverse('login'), {
            'username': 'refugee',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_register(self):
        # Test successful registration
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'email': 'new@example.com',
            'user_type': 'refugee'
        })
        self.assertRedirects(response, reverse('create_refugee_profile'))
        
        # Test duplicate username
        response = self.client.post(reverse('register'), {
            'username': 'refugee',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'email': 'new@example.com',
            'user_type': 'refugee'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')

    def test_dashboard(self):
        # Test refugee dashboard
        self.client.login(username='refugee', password='refugee123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refugees/dashboard.html')
        self.assertIn('refugee', response.context)
        
        # Test NGO dashboard
        self.client.login(username='ngo', password='ngo123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('ngo', response.context)
        
        # Test admin dashboard
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_refugees', response.context)

    def test_create_ngo_profile(self):
        # Test unauthorized access
        self.client.login(username='refugee', password='refugee123')
        response = self.client.get(reverse('create_ngo_profile'))
        self.assertRedirects(response, reverse('dashboard'))
        
        # Test successful profile creation
        new_ngo_user = User.objects.create_user(
            username='newngo',
            password='newngo123',
            user_type='ngo'
        )
        self.client.login(username='newngo', password='newngo123')
        response = self.client.post(reverse('create_ngo_profile'), {
            'organization_name': 'New NGO',
            'organization_type': 'charity',
            'location': 'New Location',
            'contact_number': '9876543210'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(NGO.objects.filter(organization_name='New NGO').exists())

    def test_create_refugee_profile(self):
        # Test unauthorized access
        self.client.login(username='ngo', password='ngo123')
        response = self.client.get(reverse('create_refugee_profile'))
        self.assertRedirects(response, reverse('dashboard'))
        
        # Test successful profile creation
        new_refugee_user = User.objects.create_user(
            username='newrefugee',
            password='newrefugee123',
            user_type='refugee'
        )
        self.client.login(username='newrefugee', password='newrefugee123')
        response = self.client.post(reverse('create_refugee_profile'), {
            'gender': 'F',
            'age': 30,
            'country_of_origin': 'New Country',
            'languages': 'English, French'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Refugee.objects.filter(user=new_refugee_user).exists())

    def test_housing_views(self):
        # Test housing list
        self.client.login(username='refugee', password='refugee123')
        response = self.client.get(reverse('housing_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refugees/housing_list.html')
        
        # Test housing detail
        response = self.client.get(reverse('housing_detail', kwargs={'pk': self.housing.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refugees/housing_detail.html')
        
        # Test housing creation (NGO only)
        self.client.login(username='ngo', password='ngo123')
        response = self.client.post(reverse('housing_create'), {
            'name': 'New Housing',
            'housing_type': 'apartment',
            'location': 'New Location',
            'capacity': 5,
            'description': 'New Description'
        })
        self.assertRedirects(response, reverse('housing_list'))
        self.assertTrue(Housing.objects.filter(name='New Housing').exists())

    def test_job_views(self):
        # Test job list
        self.client.login(username='refugee', password='refugee123')
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refugees/job_list.html')
        
        # Test job detail
        response = self.client.get(reverse('job_detail', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refugees/job_detail.html')
        
        # Test job creation (NGO only)
        self.client.login(username='ngo', password='ngo123')
        response = self.client.post(reverse('job_create'), {
            'title': 'New Job',
            'job_type': 'full_time',
            'location': 'New Location',
            'description': 'New Description',
            'deadline': timezone.now() + timedelta(days=30)
        })
        self.assertRedirects(response, reverse('job_list'))
        self.assertTrue(Job.objects.filter(title='New Job').exists())

    def test_application_views(self):
        # Test housing application
        self.client.login(username='refugee', password='refugee123')
        response = self.client.post(reverse('apply_for_housing', kwargs={'pk': self.housing.pk}))
        self.assertRedirects(response, reverse('housing_detail', kwargs={'pk': self.housing.pk}))
        self.assertTrue(HousingApplication.objects.filter(housing=self.housing, refugee=self.refugee).exists())
        
        # Test job application
        response = self.client.post(reverse('apply_for_job', kwargs={'pk': self.job.pk}))
        self.assertRedirects(response, reverse('job_detail', kwargs={'pk': self.job.pk}))
        self.assertTrue(JobApplication.objects.filter(job=self.job, refugee=self.refugee).exists())
        
        # Test application status update (NGO)
        self.client.login(username='ngo', password='ngo123')
        housing_app = HousingApplication.objects.create(
            housing=self.housing,
            refugee=self.refugee,
            status='pending'
        )
        response = self.client.post(reverse('update_housing_application_status', 
                                          kwargs={'pk': housing_app.pk, 'status': 'approved'}))
        self.assertRedirects(response, reverse('housing_application_list'))
        housing_app.refresh_from_db()
        self.assertEqual(housing_app.status, 'approved')

    def test_application_list_views(self):
        # Test housing application list
        self.client.login(username='ngo', password='ngo123')
        response = self.client.get(reverse('housing_application_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refugees/housing_application_list.html')
        
        # Test job application list
        response = self.client.get(reverse('job_application_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refugees/job_application_list.html')

    def test_profile_update_views(self):
        # Test refugee profile update
        self.client.login(username='refugee', password='refugee123')
        response = self.client.post(reverse('refugee_update', kwargs={'pk': self.refugee.pk}), {
            'gender': 'F',
            'age': 26,
            'country_of_origin': 'Updated Country',
            'languages': 'English, Spanish'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.refugee.refresh_from_db()
        self.assertEqual(self.refugee.age, 26)
        
        # Test NGO profile update
        self.client.login(username='ngo', password='ngo123')
        response = self.client.post(reverse('ngo_update', kwargs={'pk': self.ngo.pk}), {
            'organization_name': 'Updated NGO',
            'organization_type': 'charity',
            'location': 'Updated Location',
            'contact_number': '9876543210'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.ngo.refresh_from_db()
        self.assertEqual(self.ngo.organization_name, 'Updated NGO')

    def test_logout(self):
        self.client.login(username='refugee', password='refugee123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)
