from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Q
from .models import Property, PropertyImage
from .forms import PropertyForm

def owner_check(user):
    return user.is_authenticated and user.is_owner()

def property_list(request):
    """Public property listing with search and filtering"""
    properties = Property.objects.filter(is_active=True).prefetch_related('images')

    # Search functionality
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    check_in = request.GET.get('check_in', '')
    check_out = request.GET.get('check_out', '')
    guests = request.GET.get('guests', '')

    # Apply filters
    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(address__icontains=search_query)
        )

    if category_filter:
        properties = properties.filter(category=category_filter)

    if guests:
        try:
            guest_count = int(guests.split()[0])  # Extract number from "2 guests"
            properties = properties.filter(max_guests__gte=guest_count)
        except (ValueError, IndexError):
            pass

    # Context for template
    context = {
        'properties': properties,
        'search_query': search_query,
        'selected_category': category_filter,
        'check_in': check_in,
        'check_out': check_out,
        'guests': guests,
        'categories': Property.CATEGORY_CHOICES,
    }

    return render(request, 'listings/property_list.html', context)

def property_detail(request, pk):
    """Property detail with images"""
    property_obj = get_object_or_404(
        Property.objects.prefetch_related('images'), 
        pk=pk, 
        is_active=True
    )
    reviews = property_obj.reviews.all().select_related('user')
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    context = {
        'property': property_obj,
        'reviews': reviews[:3],  # Show only first 3
        'avg_rating': avg_rating,
    }
    return render(request, 'listings/property_detail.html', context)

@login_required
@user_passes_test(owner_check)
def owner_property_list(request):
    """Owner's property list with images"""
    properties = Property.objects.filter(
        owner=request.user
    ).prefetch_related('images').order_by('-created_at')
    return render(request, 'listings/property_owner_list.html', {'properties': properties})

@login_required
@user_passes_test(owner_check)
def property_create(request):
    """Create new property with multiple images"""
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
            
            # Handle multiple images upload
            images = request.FILES.getlist('images')
            for image in images:
                if image and image.size > 0:
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=image
                    )
            
            return redirect('listings:owner_property_list')
    else:
        form = PropertyForm()
    return render(request, 'listings/property_create.html', {'form': form})

@login_required
@user_passes_test(owner_check)
def property_update(request, pk):
    """Update existing property"""
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            
            # Handle multiple images upload
            images = request.FILES.getlist('images')
            for image in images:
                if image and image.size > 0:
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=image
                    )
            
            return redirect('listings:owner_property_list')
    else:
        form = PropertyForm(instance=property_obj)
    return render(request, 'listings/property_update.html', {'form': form, 'property': property_obj})

@login_required
@user_passes_test(owner_check)
def property_delete(request, pk):
    """Delete property"""
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        property_obj.delete()
        return redirect('listings:owner_property_list')
    return render(request, 'listings/property_delete_confirm.html', {'property': property_obj})
