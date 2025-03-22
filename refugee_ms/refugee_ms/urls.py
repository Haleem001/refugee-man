from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView
from refugees.views import logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='dashboard'), name='home'),
    path('', include('refugees.urls')),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='refugees/login.html'), name='login'),
 
    path('logout/', logout_view, name='logout'),
]
