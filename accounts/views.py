from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import OwnerSignUpForm, TravellerSignUpForm
from .models import User
from listings.models import Property
from bookings.models import Booking

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect based on user role
            if user.is_owner():
                return redirect('accounts:owner_dashboard')
            elif user.is_traveller():
                return redirect('accounts:traveller_dashboard')
            elif user.is_admin():
                return redirect('accounts:admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

def owner_signup(request):
    if request.method == 'POST':
        form = OwnerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:owner_dashboard')
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = OwnerSignUpForm()
    return render(request, 'accounts/register_owner.html', {'form': form})

def traveller_signup(request):
    if request.method == 'POST':
        form = TravellerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:traveller_dashboard')
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = TravellerSignUpForm()
    return render(request, 'accounts/register_traveller.html', {'form': form})

def owner_check(user):
    return user.is_authenticated and user.is_owner()

def traveller_check(user):
    return user.is_authenticated and user.is_traveller()

def admin_check(user):
    return user.is_authenticated and (user.is_admin() or user.is_staff)

@login_required
@user_passes_test(owner_check)
def owner_dashboard(request):
    properties = Property.objects.filter(owner=request.user)
    bookings = Booking.objects.filter(property__owner=request.user).select_related('property', 'traveller')
    context = {
        'properties': properties,
        'bookings': bookings,
    }
    return render(request, 'accounts/owner_dashboard.html', context)

@login_required
@user_passes_test(traveller_check)
def traveller_dashboard(request):
    bookings = Booking.objects.filter(traveller=request.user).select_related('property')
    return render(request, 'accounts/traveller_dashboard.html', {'bookings': bookings})

@login_required
@user_passes_test(admin_check)
def admin_dashboard(request):
    users = User.objects.all()
    properties = Property.objects.all()
    bookings = Booking.objects.all()
    pending_count = bookings.filter(status='PENDING').count()
    context = {
        'users': users,
        'properties': properties,
        'bookings': bookings,
        'pending_count': pending_count,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

# Redirect users to role-based dashboard after login
def login_redirect(request):
    """Redirect authenticated users to their role-specific dashboard."""
    if not request.user.is_authenticated:
        return redirect('home')
    
    if request.user.is_owner():
        return redirect('accounts:owner_dashboard')
    elif request.user.is_traveller():
        return redirect('accounts:traveller_dashboard')
    elif request.user.is_admin():
        return redirect('accounts:admin_dashboard')
    else:
        return redirect('home')

    