from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/owner/', views.owner_signup, name='owner_signup'),
    path('signup/traveller/', views.traveller_signup, name='traveller_signup'),
    path('login/', views.custom_login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/owner/', views.owner_dashboard, name='owner_dashboard'),
    path('dashboard/traveller/', views.traveller_dashboard, name='traveller_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('redirect/', views.login_redirect, name='redirect'),  # NEW
]
