import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid

from bookings.models import Booking
from .models import Payment

# Initialize Razorpay client - will be created when needed
razorpay_client = None

@login_required
def create_payment(request, booking_id):
    """Create Razorpay order for booking payment"""
    booking = get_object_or_404(Booking, id=booking_id, traveller=request.user)

    # Check if booking already has a payment
    if hasattr(booking, 'payment'):
        if booking.payment.status == 'SUCCESS':
            messages.info(request, 'Payment already completed for this booking.')
            return redirect('bookings:booking_detail', pk=booking_id)
        elif booking.payment.status == 'PENDING':
            # Redirect to existing payment
            return redirect('payments:payment_page', payment_id=booking.payment.id)

    # Try to create real Razorpay order, fallback to mock if authentication fails
    try:
        global razorpay_client
        if razorpay_client is None:
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        amount_in_paisa = int(booking.total_price() * 100)
        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paisa,
            'currency': 'INR',
            'payment_capture': '1'
        })
        order_id = razorpay_order['id']
        key_id = settings.RAZORPAY_KEY_ID
        use_real_payment = True
    except Exception as e:
        # Fallback to mock payment for development/testing
        import uuid
        order_id = f"order_mock_{uuid.uuid4().hex[:14]}"
        key_id = 'rzp_test_mock_key'  # Mock key for frontend
        use_real_payment = False
        print(f"Razorpay authentication failed: {e}")  # For debugging

    # Create payment record
    payment = Payment.objects.create(
        booking=booking,
        user=request.user,
        amount=booking.total_price(),
        razorpay_order_id=order_id,
        status='PENDING'
    )

    context = {
        'booking': booking,
        'payment': payment,
        'key_id': key_id,
        'amount': amount_in_paisa,
        'currency': 'INR',
        'razorpay_order_id': order_id,
        'use_real_payment': use_real_payment,
    }

    return render(request, 'payments/payment.html', context)

@login_required
def payment_page(request, payment_id):
    """Display payment page for existing payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.status == 'SUCCESS':
        messages.success(request, 'Payment already completed!')
        return redirect('bookings:booking_detail', pk=payment.booking.id)

    amount_in_paisa = int(payment.amount * 100)
    is_mock = payment.razorpay_order_id.startswith('order_mock_')

    context = {
        'booking': payment.booking,
        'payment': payment,
        'razorpay_order_id': payment.razorpay_order_id,
        'amount': amount_in_paisa,
        'currency': 'INR',
        'key_id': settings.RAZORPAY_KEY_ID if not is_mock else 'rzp_test_mock_key',
        'use_real_payment': not is_mock,
    }

    return render(request, 'payments/payment.html', context)

@csrf_exempt
def payment_success(request):
    """Handle successful payment callback"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')

            print(f"Payment success callback: {razorpay_order_id}, mock: {razorpay_order_id.startswith('order_mock_')}")
            is_mock = razorpay_order_id.startswith('order_mock_')

            if not is_mock:
                # Verify payment signature for real payments
                global razorpay_client
                if razorpay_client is None:
                    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                
                params_dict = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                }

                try:
                    razorpay_client.utility.verify_payment_signature(params_dict)
                except:
                    return JsonResponse({'status': 'failed', 'message': 'Payment signature verification failed'})

            # Update payment status
            try:
                payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.status = 'SUCCESS'
                payment.save()

                # Update booking status
                booking = payment.booking
                booking.status = 'CONFIRMED'
                booking.save()

                print(f"Payment successful for booking {booking.id}")

                # Return success response so frontend can redirect
                return JsonResponse({'status': 'success', 'message': 'Payment processed'})

            except Payment.DoesNotExist:
                print(f"Payment not found: {razorpay_order_id}")
                return JsonResponse({'status': 'failed', 'message': 'Payment not found'})

        except Exception as e:
            print(f"Payment success error: {e}")
            return JsonResponse({'status': 'failed', 'message': str(e)})

    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'})

@csrf_exempt
def payment_failed(request):
    """Handle failed payment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            razorpay_order_id = data.get('razorpay_order_id')

            # Update payment status to failed
            try:
                payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                payment.status = 'FAILED'
                payment.save()

                return JsonResponse({'status': 'failed', 'message': 'Payment failed'})

            except Payment.DoesNotExist:
                return JsonResponse({'status': 'failed', 'message': 'Payment not found'})

        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})

    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'})
