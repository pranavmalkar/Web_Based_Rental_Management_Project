from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from listings.models import Property
from .models import Review
from .forms import ReviewForm

@login_required
def add_review(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Check if user has already reviewed this property
    existing_review = Review.objects.filter(user=request.user, property=property_obj).first()
    if existing_review:
        messages.warning(request, 'You have already reviewed this property.')
        return redirect('listings:property_detail', pk=property_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.property = property_obj
            review.save()
            messages.success(request, 'Your review has been submitted!')
            return redirect('listings:property_detail', pk=property_id)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/add_review.html', {
        'form': form,
        'property': property_obj,
    })

def property_reviews(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    reviews = Review.objects.filter(property=property_obj).select_related('user')
    
    # Calculate average rating
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    return render(request, 'reviews/property_reviews.html', {
        'property': property_obj,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })
