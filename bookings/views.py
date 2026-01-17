from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from .models import Booking
from .forms import BookingForm
from listings.models import Property
from notifications.utils import create_notification

def traveller_check(user):
    return user.is_authenticated and user.is_traveller()

def owner_check(user):
    return user.is_authenticated and user.is_owner()

@login_required
@user_passes_test(traveller_check)
def booking_create(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id, is_active=True)
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, property=property_obj)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.traveller = request.user
            booking.property = property_obj

            # Check for overlapping bookings
            overlap = Booking.objects.filter(
                property=property_obj,
                status__in=['PENDING', 'CONFIRMED'],
                check_in__lt=booking.check_out,
                check_out__gt=booking.check_in,
            ).exists()
            
            if overlap:
                form.add_error(None, 'Selected dates are not available. Please choose different dates.')
            else:
                booking.save()
                # Create notifications
                create_notification(
                    booking.property.owner,
                    'New Booking Request',
                    f'{request.user.username} has requested to book {booking.property.title} from {booking.check_in} to {booking.check_out}.'
                )
                create_notification(
                    request.user,
                    'Booking Request Submitted',
                    f'Your booking request for {booking.property.title} has been submitted. Awaiting confirmation.'
                )
                return redirect('payments:create_payment', booking_id=booking.id)
    else:
        form = BookingForm(property=property_obj)
    
    context = {
        'form': form,
        'property': property_obj,
        'today': today,
        'tomorrow': tomorrow,
    }
    return render(request, 'bookings/booking_create.html', context)

@login_required
@user_passes_test(traveller_check)
def traveller_bookings(request):
    bookings = Booking.objects.filter(traveller=request.user).select_related('property')
    return render(request, 'bookings/booking_list_traveller.html', {'bookings': bookings})

@login_required
@user_passes_test(owner_check)
def owner_bookings(request):
    bookings = Booking.objects.filter(property__owner=request.user).select_related('property', 'traveller')
    return render(request, 'bookings/booking_list_owner.html', {'bookings': bookings})

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('property', 'traveller'), pk=pk)
    
    # Permission check
    if not (
        request.user.is_authenticated and (
            request.user.is_admin() or 
            booking.traveller == request.user or 
            booking.property.owner == request.user
        )
    ):
        raise PermissionDenied
    
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
@user_passes_test(owner_check)
def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk, property__owner=request.user)
    if booking.status == 'PENDING':
        booking.status = 'CONFIRMED'
        booking.save()
    return redirect('bookings:booking_detail', pk=pk)

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    # Permission check
    if not (
        request.user.is_authenticated and (
            request.user.is_admin() or 
            booking.traveller == request.user or 
            booking.property.owner == request.user
        )
    ):
        raise PermissionDenied
    
    if booking.status != 'CANCELLED':
        booking.status = 'CANCELLED'
        booking.save()
    
    return redirect('bookings:booking_detail', pk=pk)
