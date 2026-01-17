from django.shortcuts import render, redirect
from django.contrib import messages
from listings.models import Property

def home(request):
    """Home page view with featured properties"""
    featured_properties = Property.objects.filter(is_active=True).prefetch_related('images')[:6]
    context = {
        'featured_properties': featured_properties,
    }
    return render(request, 'home.html', context)

def about(request):
    """About Us page"""
    return render(request, 'about.html')

def contact(request):
    """Contact Us page"""
    if request.method == 'POST':
        # Here you would typically send an email or save to database
        # For now, we'll just show a success message
        from django.contrib import messages
        messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
        return redirect('contact')

    return render(request, 'contact.html')