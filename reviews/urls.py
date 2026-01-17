from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('property/<int:property_id>/add/', views.add_review, name='add_review'),
    path('property/<int:property_id>/reviews/', views.property_reviews, name='property_reviews'),
]